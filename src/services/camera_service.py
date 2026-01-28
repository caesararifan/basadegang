import cv2
import os
from ultralytics import YOLO
from src.utils.logger import get_logger

class CameraService:
    def __init__(self):
        self.logger = get_logger()
        
        # --- KONFIGURASI KAMERA ---
        # Note: Ganti ke 0 jika nanti sudah pakai Kamera USB/Raspi Cam asli
        # self.camera_source = 0 
        self.camera_source = "http://192.168.1.16:4747/video" 
        
        self.cap = cv2.VideoCapture(self.camera_source)
        
        if not self.cap.isOpened():
            self.logger.critical(f"Kamera tidak terdeteksi di {self.camera_source}!")
        
        # --- LOAD AI ---
        model_path = "models/best.pt" if os.path.exists("models/best.pt") else "yolov8n.pt"
        self.logger.info(f"[AI] Loading Model: {model_path} ...")
        self.model = YOLO(model_path)

    def get_frame(self):
        """Ambil 1 frame mentah untuk QR atau AI"""
        if not self.cap.isOpened():
            self.logger.error("Kamera putus, mencoba reconnect...")
            self.cap.open(self.camera_source)
            
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def analyze_snapshot(self, frame):
        """
        Analisa 1 gambar diam.
        Return: (label_terdeteksi, frame_hasil_gambar)
        """
        # Jalankan AI (Predict mode, bukan Track)
        # conf=0.4 artinya minimal 40% yakin
        results = self.model.predict(frame, conf=0.4, verbose=False)
        
        detected_label = "Unknown"
        annotated_frame = frame # Default kalau tidak ada deteksi
        
        # Cek hasil deteksi
        if len(results) > 0:
            annotated_frame = results[0].plot() # Gambar kotak otomatis
            
            if len(results[0].boxes) > 0:
                # Ambil objek dengan confidence tertinggi (urutan pertama)
                box = results[0].boxes[0]
                cls_id = int(box.cls)
                detected_label = results[0].names[cls_id]
                
                # Debugging log
                self.logger.info(f"[AI] Terdeteksi: {detected_label} (Conf: {box.conf.item():.2f})")

        return detected_label, annotated_frame

    def release(self):
        self.cap.release()