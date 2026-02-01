import cv2
import os
import numpy as np
from PIL import Image

class FaceRecognizer:
    def __init__(self):
        self.face_cascade_path = "resources/haarcascade_frontalface_default.xml"
        self.training_data_dir = "data/training_images"
        self.model_dir = "data/models"
        self.model_path = os.path.join(self.model_dir, "trainer.yml")
        
        # Ensure directories exist
        os.makedirs(self.training_data_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.face_cascade = cv2.CascadeClassifier(self.face_cascade_path)
        if self.face_cascade.empty():
            print(f"Error: Could not load cascade classifier from {self.face_cascade_path}")
            # Fallback to local if running from root without resources prefix
            if os.path.exists("haarcascade_frontalface_default.xml"):
                 self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def capture_images(self, enrollment, name, callback=None):
        cam = cv2.VideoCapture(0)
        sample_num = 0
        
        while True:
            ret, img = cam.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sample_num += 1
                
                # Save image
                file_name = f"{name}.{enrollment}.{sample_num}.jpg"
                cv2.imwrite(os.path.join(self.training_data_dir, file_name), gray[y:y+h, x:x+w])
                
                cv2.imshow('Face Capture', img)
            
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sample_num >= 60: # Stop after 60 samples
                break
        
        cam.release()
        cv2.destroyAllWindows()
        return True

    def train_model(self):
        if not os.listdir(self.training_data_dir):
            return False, "No training data found."

        image_paths = [os.path.join(self.training_data_dir, f) for f in os.listdir(self.training_data_dir)]
        face_samples = []
        ids = []

        for image_path in image_paths:
            try:
                pil_image = Image.open(image_path).convert('L')
                image_np = np.array(pil_image, 'uint8')
                
                # Expecting filename format: Name.Enrollment.SampleNum.jpg
                filename = os.path.split(image_path)[-1]
                parts = filename.split(".")
                id = int(parts[1])
                
                faces = self.face_cascade.detectMultiScale(image_np)
                for (x, y, w, h) in faces:
                    face_samples.append(image_np[y:y+h, x:x+w])
                    ids.append(id)
            except Exception as e:
                print(f"Skipping file {image_path}: {e}")

        if not ids:
             return False, "No valid faces found in training data."

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(face_samples, np.array(ids))
        recognizer.save(self.model_path)
        return True, "Model trained successfully."

    def recognize_face(self):
        if not os.path.exists(self.model_path):
             return False, "Model not trained yet."

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(self.model_path)
        
        cam = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        recognized_students = [] # List of tuples (enrollment, confidence)
        
        while True:
            ret, img = cam.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
            
            for (x, y, w, h) in faces:
                id, conf = recognizer.predict(gray[y:y+h, x:x+w])
                
                # Check confidence (lower is better for LBPH)
                if conf < 100:
                    name = str(id) # Ideally we should fetch name from DB using this ID, doing it in caller
                    confidence = "  {0}%".format(round(100 - conf))
                    
                    # We return the ID, caller will handle name lookup
                    recognized_students.append(str(id))
                    
                    cv2.putText(img, str(id), (x+5, y-5), font, 1, (255, 255, 255), 2)
                    cv2.putText(img, str(confidence), (x+5, y+h-5), font, 1, (255, 255, 0), 1)
                else:
                    name = "unknown"
                    cv2.putText(img, name, (x+5, y-5), font, 1, (255, 255, 255), 2)
                
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv2.imshow('Face Recognition', img)
            
            k = cv2.waitKey(10) & 0xff
            if k == 27: # Press 'ESC' to exit
                break
        
        cam.release()
        cv2.destroyAllWindows()
        return list(set(recognized_students)) # Return unique IDs found
