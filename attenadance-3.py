# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 11:08:18 2025

@author: deepj
"""

#!/usr/bin/env python3
"""Question Paper Generator + Attendance Manager - PyQt5

Dependencies:
  pip install PyQt5 reportlab PyPDF2

Features:
 - Question bank (add/edit/delete)
 - Generate question papers (PDF export)
 - Attendance system (Morning / Afternoon / Evening)
 - Load student names automatically from PDF, TXT, or CSV
 - Saves attendance as text logs (no DB)

Author: Deepjyoti Das (2025)
"""

import sys
import os
import random
import sqlite3
import csv
from datetime import datetime
from collections import defaultdict
from PyPDF2 import PdfReader

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QSpinBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QFormLayout
)
from PyQt5.QtCore import Qt

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DB_FILE = 'questions.db'
PAPERS_DIR = 'generated_papers'
ATTENDANCE_DIR = 'attendance_logs'


# ---------------------- File Helpers ----------------------
def extract_names_from_pdf(pdf_path):
    """Extract student names from simple text-based PDF."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        names = [line for line in lines if any(ch.isalpha() for ch in line)]
        return names
    except Exception as e:
        print("Error reading PDF:", e)
        return []


def extract_names_from_txt(txt_path):
    try:
        with open(txt_path, "r", encoding="utf8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines
    except Exception as e:
        print("Error reading TXT:", e)
        return []


def extract_names_from_csv(csv_path):
    names = []
    try:
        with open(csv_path, "r", encoding="utf8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                name = row[0].strip()
                if name:
                    names.append(name)
        return names
    except Exception as e:
        print("Error reading CSV:", e)
        return []


# ---------------------- Database helper ----------------------
class QuestionDB:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter TEXT,
                subject TEXT,
                class TEXT,
                marks INTEGER,
                difficulty TEXT,
                qtype TEXT,
                text TEXT,
                answer TEXT,
                created_at TEXT
            )
        ''')
        self.conn.commit()

    def add_question(self, q):
        cur = self.conn.cursor()
        cur.execute('''
            INSERT INTO questions (chapter, subject, class, marks, difficulty, qtype, text, answer, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (q['chapter'], q['subject'], q['class'], q['marks'],
              q['difficulty'], q['qtype'], q['text'], q['answer'], q['created_at']))
        self.conn.commit()
        return cur.lastrowid


# ---------------------- PDF Export ----------------------
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def export_pdf(filename, paper_meta, questions, include_answers=False):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin_x = 50
    y = height - 50

    c.setFont('Helvetica-Bold', 16)
    c.drawString(margin_x, y, paper_meta.get('title', 'Generated Paper'))
    c.setFont('Helvetica', 10)
    y -= 20
    c.drawString(margin_x, y,
                 f"Total Marks: {paper_meta.get('total_marks', '')}    Duration: {paper_meta.get('duration_minutes', '')} mins")
    y -= 20
    c.drawString(margin_x, y, f"Generated: {paper_meta.get('generated_at', '')}")
    y -= 30

    c.setFont('Helvetica', 12)
    for i, q in enumerate(questions):
        text = f"Q{i+1}. {q['text']} ({q['marks']} marks)"
        lines = split_text_to_lines(text, 80)
        for line in lines:
            if y < 80:
                c.showPage()
                y = height - 50
                c.setFont('Helvetica', 12)
            c.drawString(margin_x, y, line)
            y -= 18
        y -= 6
        if include_answers:
            ans_lines = split_text_to_lines('Ans: ' + q.get('answer', ''), 80)
            c.setFont('Helvetica-Oblique', 10)
            for line in ans_lines:
                if y < 80:
                    c.showPage()
                    y = height - 50
                    c.setFont('Helvetica-Oblique', 10)
                c.drawString(margin_x + 20, y, line)
                y -= 14
            c.setFont('Helvetica', 12)
            y -= 6
    c.save()


def split_text_to_lines(text, max_chars):
    words = text.split()
    lines = []
    cur = ''
    for w in words:
        if len(cur) + len(w) + 1 <= max_chars:
            cur = (cur + ' ' + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------- Main Window ----------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Teacher Assistant - PyQt5')
        self.resize(1100, 750)

        self.db = QuestionDB()
        ensure_dir(PAPERS_DIR)
        ensure_dir(ATTENDANCE_DIR)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self._init_attendance_tab()

        self.att_records = []

    # ------------------ Attendance Tab ------------------
    def _init_attendance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        form = QFormLayout()
        self.att_class = QLineEdit('10')
        self.att_subject = QLineEdit('Mathematics')
        self.att_session = QComboBox()
        self.att_session.addItems(['Morning', 'Afternoon', 'Evening'])
        form.addRow('Class:', self.att_class)
        form.addRow('Subject:', self.att_subject)
        form.addRow('Session:', self.att_session)
        layout.addLayout(form)

        self.table_att = QTableWidget(0, 2)
        self.table_att.setHorizontalHeaderLabels(['Student Name', 'Status'])
        layout.addWidget(self.table_att)

        form2 = QHBoxLayout()
        btn_load_file = QPushButton('📂 Load Student List (PDF/TXT/CSV)')
        btn_mark_all_present = QPushButton('Mark All Present')
        btn_save = QPushButton('Save Attendance Log')
        form2.addWidget(btn_load_file)
        form2.addWidget(btn_mark_all_present)
        form2.addWidget(btn_save)
        layout.addLayout(form2)

        tab.setLayout(layout)
        self.tabs.addTab(tab, 'Attendance')

        btn_load_file.clicked.connect(self.load_students_from_file)
        btn_mark_all_present.clicked.connect(self.mark_all_present)
        btn_save.clicked.connect(self.save_attendance_log)

    def load_students_from_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select File', '', 'All Supported (*.pdf *.txt *.csv);;PDF Files (*.pdf);;Text Files (*.txt);;CSV Files (*.csv)'
        )
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            names = extract_names_from_pdf(path)
        elif ext == ".txt":
            names = extract_names_from_txt(path)
        elif ext == ".csv":
            names = extract_names_from_csv(path)
        else:
            QMessageBox.warning(self, "Unsupported", "Please select a PDF, TXT, or CSV file.")
            return

        if not names:
            QMessageBox.warning(self, "No Names Found", "Could not find any student names.")
            return

        self.att_records = [{'student': n, 'status': 'Present'} for n in names]
        self.refresh_attendance_table()
        QMessageBox.information(self, 'Loaded', f'{len(names)} student names loaded.')

    def refresh_attendance_table(self):
        self.table_att.setRowCount(0)
        for rec in self.att_records:
            row = self.table_att.rowCount()
            self.table_att.insertRow(row)
            self.table_att.setItem(row, 0, QTableWidgetItem(rec['student']))
            self.table_att.setItem(row, 1, QTableWidgetItem(rec['status']))
        self.table_att.resizeColumnsToContents()

    def mark_all_present(self):
        for rec in self.att_records:
            rec['status'] = 'Present'
        self.refresh_attendance_table()

    def save_attendance_log(self):
        if not self.att_records:
            QMessageBox.warning(self, 'Empty', 'No attendance records to save.')
            return
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        class_name = self.att_class.text().strip()
        session = self.att_session.currentText()
        fname = os.path.join(ATTENDANCE_DIR, f"{class_name}_{session}_{now}.txt")
        with open(fname, 'w', encoding='utf8') as f:
            f.write(f"Class: {class_name}\nSubject: {self.att_subject.text()}\nSession: {session}\nDate: {datetime.now()}\n\n")
            for rec in self.att_records:
                f.write(f"{rec['student']} - {rec['status']}\n")
        QMessageBox.information(self, 'Saved', f'Attendance log saved:\n{fname}')


# ---------------------- Run App ----------------------
def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
