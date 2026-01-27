import cv2
import os
from ultralytics import YOLO
from src.utils.logger import get_logger

class CameraService:
    def __init__(self):
        self.logger = get_logger()
        
        # --- KONFIGURASI KAMERA ---
        # Pastikan IP DroidCam ini SAMA PERSIS dengan di HP kamu
        self.cap = cv2.VideoCapture("http://192.168.100.31:4747/video")
        
        if not self.cap.isOpened():
            self.logger.critical("Kamera tidak terdeteksi! Cek IP DroidCam.")
        
        # --- LOAD AI ---
        model_path = "models/best.pt" if os.path.exists("models/best.pt") else "yolov8n.pt"
        self.logger.info(f"[AI] Loading Model: {model_path} ...")
        self.model = YOLO(model_path)
        
        # --- SETTING GARIS ---
        self.line_y_position = 0.5 
        self.counted_ids = set()

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def process_ai(self, frame):
        height, width, _ = frame.shape
        line_y = int(height * self.line_y_position)
        new_trash_count = 0
        
        # 1. Gambar Garis Hijau (Batas Hitung)
        cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 0), 2)

        # 2. Jalankan AI (Mode Debug: Deteksi SEMUA benda)
        # conf=0.3 artinya 30% yakin sudah dianggap ada
        results = self.model.track(frame, persist=True, conf=0.3, verbose=False)
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            class_ids = results[0].boxes.cls.int().cpu().tolist() # Ambil ID Jenis Benda

            for box, track_id, cls_id in zip(boxes, track_ids, class_ids):
                x, y, w, h = box
                
                # Ambil nama benda (misal: 'bottle', 'cup', 'person')
                obj_name = self.model.names[cls_id]

                # --- VISUALISASI DEBUG (GAMBAR KOTAK & NAMA) ---
                # Warna kotak: Biru (Benda biasa), Merah (Sampah target)
                color = (255, 0, 0) 
                if cls_id in [39, 41]: # 39=Bottle, 41=Cup
                    color = (0, 0, 255) # Jadi Merah kalau botol/gelas

                # Gambar Kotak
                cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), color, 2)
                
                # Tulis Nama Benda di Layar
                label = f"{obj_name} ({cls_id})"
                cv2.putText(frame, label, (int(x), int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # --- LOGIC HITUNG (HANYA BOTOL & GELAS) ---
                if cls_id in [39, 41]: 
                    # Cek apakah titik tengah (y) melewati garis (line_y)
                    if y > line_y and track_id not in self.counted_ids:
                        self.counted_ids.add(track_id)
                        new_trash_count += 1
                        
                        # Efek Visual kalau Berhasil Dihitung
                        cv2.circle(frame, (int(x), int(y)), 15, (0, 255, 0), -1)
                        print(f"[SUKSES] {obj_name} masuk! Total sesi nambah.")

        return frame, new_trash_count

    def reset_counter(self):
        self.counted_ids.clear()

    def release(self):
        self.cap.release()