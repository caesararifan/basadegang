import time
import cv2
import os
from src.utils.logger import get_logger
from src.services.camera_service import CameraService
from src.services.serial_service import SerialService
from src.services.api_service import ApiService
from src.services.qr_service import QrService

class MainController:
    def __init__(self):
        self.logger = get_logger()
        self.logger.info("Menginisialisasi Modules...")
        
        self.camera = CameraService()
        self.serial = SerialService()
        self.api = ApiService()
        self.qr = QrService()
        
        # Config
        self.timeout_limit = int(os.getenv("TIMEOUT_SECONDS", 15))
        self.points_per_item = int(os.getenv("POINTS_PER_ITEM", 50))
        
        # State Variables
        # self.state = "SCAN_MODE" # SCAN_MODE -> COUNTING_MODE
        # self.current_user = None
        self.state = "COUNTING_MODE" 
        self.current_user = "USER-TESTING-MANUAL"
        self.total_trash_session = 0
        self.last_activity_time = time.time()

    def run(self):
        self.logger.info("=== SYSTEM READY ===")
        
        while True:
            frame = self.camera.get_frame()
            if frame is None:
                break
            
            # --- MODE 1: SCAN QR ---
            if self.state == "SCAN_MODE":
                # Tampilkan text instruksi di layar
                cv2.putText(frame, "SCAN QR CODE ANDA", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
                qr_data = self.qr.scan(frame)
                if qr_data:
                    self.start_session(qr_data)

            # --- MODE 2: HITUNG SAMPAH ---
            elif self.state == "COUNTING_MODE":
                # Proses AI (YOLO)
                frame, new_trash = self.camera.process_ai(frame)
                
                if new_trash > 0:
                    self.total_trash_session += new_trash
                    self.last_activity_time = time.time() # Reset timer timeout
                    self.logger.info(f"Sampah Masuk! Total Sesi: {self.total_trash_session}")
                
                # Tampilkan info di layar
                cv2.putText(frame, f"User: {self.current_user}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Total: {self.total_trash_session}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Cek Timeout (User pergi/selesai)
                if time.time() - self.last_activity_time > self.timeout_limit:
                    self.end_session()

            # Tampilkan Window (Tekan Q untuk keluar)
            cv2.imshow("Smart Trash Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.camera.release()
        cv2.destroyAllWindows()

    def start_session(self, user_id):
        self.logger.info(f"Memulai Sesi untuk User: {user_id}")
        self.current_user = user_id
        self.total_trash_session = 0
        self.camera.reset_counter()
        
        # Buka Servo
        if self.serial.send_command("OPEN"):
            self.state = "COUNTING_MODE"
            self.last_activity_time = time.time()
        else:
            self.logger.error("Gagal membuka Servo!")

    def end_session(self):
        self.logger.info("Sesi Berakhir (Timeout). Menutup Servo...")
        
        # Tutup Servo
        self.serial.send_command("CLOSE")
        
        # Hitung Poin
        points = self.total_trash_session * self.points_per_item
        
        # Kirim Data ke VPS
        if self.total_trash_session > 0:
            self.api.send_transaction(self.current_user, self.total_trash_session, points)
        else:
            self.logger.info("Tidak ada sampah masuk. Transaksi dibatalkan.")

        # Reset State
        self.state = "SCAN_MODE"
        self.current_user = None