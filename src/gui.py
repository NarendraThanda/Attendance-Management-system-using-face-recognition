import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import cv2
import csv
import os
import numpy as np
from PIL import Image, ImageTk
import datetime
import time

from src.database import DatabaseManager
from src.recognizer import FaceRecognizer

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Management System using Face Recognition")
        self.root.geometry('1280x720')
        self.root.configure(background='grey80')
        
        self.db = DatabaseManager()
        self.recognizer = FaceRecognizer()

        self._build_ui()

    def _build_ui(self):
        # Header
        title = tk.Label(self.root, text="Attendance Management System", bg="black", fg="white", 
                         font=('times', 30, 'bold'), width=50, height=3)
        title.place(x=80, y=20)

        # Status Label
        self.status_label = tk.Label(self.root, text="System Ready", bg="Green", fg="white", 
                                     width=30, height=2, font=('times', 15))
        self.status_label.place(x=450, y=160)

        # Inputs for Registration
        tk.Label(self.root, text="Enter Enrollment:", width=15, height=2, fg="black", bg="grey", 
                 font=('times', 15, 'bold')).place(x=200, y=250)
        self.txt_enrollment = tk.Entry(self.root, width=20, bg="white", fg="black", font=('times', 25))
        self.txt_enrollment.place(x=550, y=250)

        tk.Label(self.root, text="Enter Name:", width=15, height=2, fg="black", bg="grey", 
                 font=('times', 15, 'bold')).place(x=200, y=350)
        self.txt_name = tk.Entry(self.root, width=20, bg="white", fg="black", font=('times', 25))
        self.txt_name.place(x=550, y=350)

        # Buttons
        tk.Button(self.root, text="Clear", command=lambda: self.txt_enrollment.delete(0, 'end'), 
                  fg="white", bg="black", width=10, font=('times', 15, 'bold')).place(x=950, y=250)
        tk.Button(self.root, text="Clear", command=lambda: self.txt_name.delete(0, 'end'), 
                  fg="white", bg="black", width=10, font=('times', 15, 'bold')).place(x=950, y=350)

        # Main Actions
        tk.Button(self.root, text="Take Images", command=self.take_images, fg="black", bg="SkyBlue1", 
                  width=20, height=3, font=('times', 15, 'bold')).place(x=100, y=500)
        
        tk.Button(self.root, text="Train Images", command=self.train_images, fg="black", bg="SkyBlue1", 
                  width=20, height=3, font=('times', 15, 'bold')).place(x=400, y=500)
        
        tk.Button(self.root, text="Automatic Attendance", command=self.automatic_attendance, fg="black", bg="SkyBlue1", 
                  width=20, height=3, font=('times', 15, 'bold')).place(x=700, y=500)

        tk.Button(self.root, text="View Students", command=self.view_students, fg="black", bg="SkyBlue1", 
                  width=20, height=3, font=('times', 15, 'bold')).place(x=1000, y=500)

    def update_status(self, message, color="Green"):
        self.status_label.configure(text=message, bg=color)

    def take_images(self):
        enrollment = self.txt_enrollment.get()
        name = self.txt_name.get()
        
        if enrollment == '' or name == '':
            messagebox.showwarning("Warning", "Enrollment and Name are required!")
            return
            
        # Add to DB first
        success, msg = self.db.add_student(enrollment, name)
        if not success:
            if "already exists" in msg:
                 # Proceed with image capture even if student exists (maybe retraining)
                 pass
            else:
                 messagebox.showerror("Error", msg)
                 return

        self.update_status(f"Capturing Images for {name}...")
        self.root.update()
        
        try:
            self.recognizer.capture_images(enrollment, name)
            self.update_status(f"Images Saved for {name}", "Green")
            messagebox.showinfo("Success", f"Images saved for {name}")
        except Exception as e:
            self.update_status(f"Error: {str(e)}", "Red")

    def train_images(self):
        self.update_status("Training Model...", "Yellow")
        self.root.update()
        
        success, msg = self.recognizer.train_model()
        if success:
            self.update_status("Model Trained Successfully", "Green")
            messagebox.showinfo("Success", msg)
        else:
            self.update_status("Training Failed", "Red")
            messagebox.showerror("Error", msg)

    def automatic_attendance(self):
        subject = simpledialog.askstring("Input", "Enter Subject Name:")
        if not subject:
            return

        self.update_status("Taking Attendance...", "Yellow")
        self.root.update()
        
        present_ids = self.recognizer.recognize_face()
        if not present_ids:
             self.update_status("No faces recognized", "Red")
             return

        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        count = 0
        for enrollment in present_ids:
            # Get name
            cursor.execute("SELECT name FROM students WHERE enrollment=?", (enrollment,))
            res = cursor.fetchone()
            if res:
                name = res[0]
                self.db.mark_attendance(enrollment, name, subject)
                count += 1
        
        conn.close()
        self.update_status(f"Attendance Marked for {count} students", "Green")
        messagebox.showinfo("Success", f"Attendance marked for {count} students.")


    def view_students(self):
        students = self.db.get_student_details()
        
        win = tk.Toplevel(self.root)
        win.title("Registered Students")
        win.geometry("600x400")
        
        # Headers
        headers = ["Enrollment", "Name", "Date", "Time"]
        for col, h in enumerate(headers):
            tk.Label(win, text=h, font=('bold', 12), borderwidth=1, relief="solid", width=15).grid(row=0, column=col)
            
        for i, student in enumerate(students):
            for j, val in enumerate(student):
                tk.Label(win, text=val, borderwidth=1, relief="solid", width=15).grid(row=i+1, column=j)

