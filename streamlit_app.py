import streamlit as st
import cv2
import numpy as np
import datetime
from PIL import Image
import os
import shutil

# Local Modules (we reuse the logic but adapt for Streamlit)
from src.database import DatabaseManager

# Initialize standard database
db = DatabaseManager()

# --- Page Config ---
st.set_page_config(page_title="Attendance System", layout="wide")

# --- Helper Functions for Streamlit ---
def save_uploaded_image(uploaded_file, name, enrollment):
    # Ensure directory exists
    save_dir = "data/training_images"
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        image = Image.open(uploaded_file).convert('L')
        image_np = np.array(image, 'uint8')
        
        # Save usually requires multiple samples for training
        # For this web demo, we will just save one or generate variants
        # In a real deployed app, capturing 60 frames via web is harder without webrtc
        # We will save this SINGLE image as a "sample"
        
        # Checking existing count to increment sample num
        existing_files = [f for f in os.listdir(save_dir) if f.startswith(f"{name}.{enrollment}")]
        sample_num = len(existing_files) + 1
        
        file_name = f"{name}.{enrollment}.{sample_num}.jpg"
        save_path = os.path.join(save_dir, file_name)
        
        cv2.imwrite(save_path, image_np)
        return True, f"Saved sample {sample_num}"
    except Exception as e:
        return False, str(e)

def train_model():
    # Reuse logic from recognizer.py but adapted
    training_dir = "data/training_images"
    model_dir = "data/models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "trainer.yml")
    
    if not os.path.exists(training_dir) or not os.listdir(training_dir):
        return False, "No training data found."

    image_paths = [os.path.join(training_dir, f) for f in os.listdir(training_dir)]
    face_samples = []
    ids = []
    
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    for image_path in image_paths:
        try:
            pil_image = Image.open(image_path).convert('L')
            image_np = np.array(pil_image, 'uint8')
            
            filename = os.path.split(image_path)[-1]
            parts = filename.split(".")
            id_val = int(parts[1])
            
            faces = detector.detectMultiScale(image_np)
            for (x, y, w, h) in faces:
                face_samples.append(image_np[y:y+h, x:x+w])
                ids.append(id_val)
        except Exception:
            pass

    if not ids:
        return False, "No valid faces found."

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(face_samples, np.array(ids))
    recognizer.save(model_path)
    return True, "Model trained successfully."

def recognize_from_image(uploaded_file):
    model_path = "data/models/trainer.yml"
    if not os.path.exists(model_path):
        return False, "Model not trained."
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_path)
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    image = Image.open(uploaded_file).convert('L')
    image_np = np.array(image, 'uint8')
    faces = detector.detectMultiScale(image_np, 1.2, 5)
    
    recognized_ids = []
    
    for (x, y, w, h) in faces:
        id_val, conf = recognizer.predict(image_np[y:y+h, x:x+w])
        if conf < 100:
            recognized_ids.append(str(id_val))
            
    return True, recognized_ids

# --- Sidebar ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Register Student", "Train Model", "Mark Attendance", "View Records"])

# --- Pages ---
if page == "Home":
    st.title("Attendance Management System")
    st.write("Welcome to the Face Recognition Attendance System (Web Version).")
    st.info("Note: For Vercel deployment, data is ephemeral (resets on restart) unless connected to Cloud Storage.")

elif page == "Register Student":
    st.header("Register New Student")
    enrollment = st.text_input("Enrollment ID")
    name = st.text_input("Student Name")
    
    img_file = st.camera_input("Take a picture")
    
    if st.button("Save Profile"):
        if enrollment and name and img_file:
            # 1. Register in DB
            success, msg = db.add_student(enrollment, name)
            if success or "already exists" in msg:
                # 2. Save Image
                ok, img_msg = save_uploaded_image(img_file, name, enrollment)
                if ok:
                    st.success(f"Registered {name} & {img_msg}")
                else:
                    st.error(f"Error saving image: {img_msg}")
            else:
                st.error(msg)
        else:
            st.warning("Please fill all fields and take a photo.")

elif page == "Train Model":
    st.header("Train Recognition Model")
    if st.button("Start Training"):
        with st.spinner("Training..."):
            success, msg = train_model()
            if success:
                st.success(msg)
            else:
                st.error(msg)

elif page == "Mark Attendance":
    st.header("Mark Attendance")
    subject = st.text_input("Subject Name")
    
    img_file = st.camera_input("Scan Face for Attendance")
    
    if st.button("Mark Present"):
        if subject and img_file:
            success, result = recognize_from_image(img_file)
            if success:
                if result:
                    present_names = []
                    for enroll in set(result):
                        # Fetch name
                        rows = db.get_student_details()
                        student_name = "Unknown"
                        for r in rows: 
                            if str(r[0]) == str(enroll):
                                student_name = r[1]
                                break
                        
                        db.mark_attendance(enroll, student_name, subject)
                        present_names.append(student_name)
                    
                    st.success(f"Marked Present: {', '.join(present_names)}")
                else:
                    st.warning("Face not recognized.")
            else:
                st.error(result)
        else:
            st.warning("Enter subject and take photo.")

elif page == "View Records":
    st.header("Attendance Records")
    subject_filter = st.text_input("Filter by Subject")
    if subject_filter:
        data = db.get_attendance_log(subject_filter)
        if data:
            st.table(data)
        else:
            st.info("No records found.")
    else:
        st.write("Enter a subject to view logs.")
