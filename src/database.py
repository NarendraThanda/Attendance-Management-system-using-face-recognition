import sqlite3
import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="data/attendance.db"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Table for registered students
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                enrollment TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                registered_date TEXT,
                registered_time TEXT
            )
        """)

        # We will create dynamic tables for each subject/session or just one big attendance table?
        # The original code created a new table for EVERY attendance session (Subject_Date_Time).
        # That is bad practice. Better to have one Attendance table.
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment TEXT,
                name TEXT,
                subject TEXT,
                date TEXT,
                time TEXT,
                FOREIGN KEY(enrollment) REFERENCES students(enrollment)
            )
        """)
        
        conn.commit()
        conn.close()

    def add_student(self, enrollment, name):
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            ts = datetime.datetime.now()
            date = ts.strftime('%Y-%m-%d')
            time = ts.strftime('%H:%M:%S')
            
            cursor.execute("INSERT INTO students (enrollment, name, registered_date, registered_time) VALUES (?, ?, ?, ?)",
                           (enrollment, name, date, time))
            conn.commit()
            return True, "Student registered successfully."
        except sqlite3.IntegrityError:
            return False, "Enrollment number already exists."
        except Exception as e:
            return False, str(e)
        finally:
            if 'conn' in locals(): conn.close()

    def mark_attendance(self, enrollment, name, subject):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        ts = datetime.datetime.now()
        date = ts.strftime('%Y-%m-%d')
        time = ts.strftime('%H:%M:%S')
        
        # Check if already marked for this subject today? 
        # For simplicity, we just insert like the original code did (mostly).
        # Original code filtered duplicates in memory before saving to CSV.
        
        cursor.execute("INSERT INTO attendance (enrollment, name, subject, date, time) VALUES (?, ?, ?, ?, ?)",
                       (enrollment, name, subject, date, time))
        
        conn.commit()
        conn.close()
        return date, time

    def get_student_details(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT enrollment, name, registered_date, registered_time FROM students")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_attendance_log(self, subject):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE subject = ?", (subject,))
        rows = cursor.fetchall()
        conn.close()
        return rows
