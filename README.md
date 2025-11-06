🧑‍🏫 Teacher Assistant - Question Paper Generator + Attendance Manager (PyQt5)
📘 Description

A simple desktop application for teachers, built with Python and PyQt5, to generate question papers and manage student attendance — all without needing any database server.
It supports PDF export, student name auto-import from files, and log-based attendance tracking.

✨ Features
📄 Question Paper Generator

Add, edit, or delete questions stored locally in SQLite (questions.db)

Supports attributes like chapter, subject, class, marks, difficulty, and question type

Automatically generate printable question papers (PDF)

Option to include answers in the exported paper

Randomized question selection for variety

🧍 Attendance Manager

Mark attendance for Morning, Afternoon, or Evening sessions

Auto-load student names from:

.pdf (text-based)

.txt

.csv

Option to mark all present

Saves attendance logs as .txt files (no database needed)

🧰 Installation
🪄 Prerequisites

Install Python 3.7+ and run:

pip install PyQt5 reportlab PyPDF2

📦 Clone the Repository
git clone https://github.com/deepjyoti-dev/teacher-assistant.git
cd teacher-assistant

🚀 Usage

Run the main script:

python main.py

🖥️ Interface Tabs

Attendance: Load student names, mark attendance, and export logs

(Coming soon): Question Bank and Paper Generator tabs for easy test creation

🗂️ File Structure
teacher-assistant/
├── main.py                # Main application script
├── questions.db           # SQLite database (auto-created)
├── generated_papers/      # PDF question papers
├── attendance_logs/       # Saved attendance files
└── README.md              # Project documentation

🧩 Dependencies

PyQt5

reportlab

PyPDF2

📅 Version

v1.0.0 – Initial release (Attendance + PDF generation)

👨‍💻 Author

Deepjyoti Das
📅 2025

💡 Future Enhancements

 Add Question Bank Management UI (Add/Edit/Delete)

 Support randomized question paper generation

 Add search/filter for questions
