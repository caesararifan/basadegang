import time
from src.services.camera_service import CameraService
from src.services.serial_service import SerialService
from src.services.qr_service import QrService
from src.services.api_service import ApiService
from src.utils.logger import get_logger

class MainController:
    def __init__(self):
        self.logger = get_logger()
        
        # 1. Inisialisasi Semua Service
        try:
            self.camera = CameraService()
            self.serial = SerialService()
            self.qr = QrService()
            self.api = ApiService()
            self.logger.info("[SYSTEM] Semua service berhasil di-load.")
        except Exception as e:
            self.logger.critical(f"[SYSTEM] Gagal inisialisasi: {e}")
            exit(1)

    def start(self):
        """Loop utama aplikasi"""
        self.logger.info("[SYSTEM] System Ready. Menunggu User...")
        
        # Pastikan Servo tertutup saat awal nyala
        self.serial.send_command("CLOSE") 

        try:
            while True:
                # Loop ini akan terus berjalan menunggu user baru
                self.run_session()
                
                # Jeda sebentar sebelum siap menerima user berikutnya
                time.sleep(2) 
                
        except KeyboardInterrupt:
            self.stop()

    def run_session(self):
        """Menjalankan 1 sesi lengkap dari Scan sampai Tutup"""
        
        # --- STEP 1: MENUNGGU SCAN QR ---
        # Kita ambil frame terus menerus sampai QR ditemukan
        user_qr_data = None
        self.logger.info("--- [STEP 1] Menunggu Scan QR... ---")
        
        while user_qr_data is None:
            frame = self.camera.get_frame()
            if frame is None: continue # Skip jika kamera belum siap
            
            # Cek QR di frame tersebut
            user_qr_data = self.qr.scan(frame)
            
            # Optional: Tambahkan timeout jika tidak ada yg scan (biar gak infinite loop)
            time.sleep(0.1) 

        self.logger.info(f"[QR] User Terdeteksi: {user_qr_data}")
        
        # --- STEP 2: BUKA TEMPAT SAMPAH ---
        self.logger.info("--- [STEP 2] Membuka Servo... ---")
        self.serial.send_command("OPEN")
        
        # --- STEP 3: WAKTU BUANG SAMPAH ---
        self.logger.info("--- [STEP 3] Silakan Buang Sampah (5 Detik) ---")
        time.sleep(5) # Waktu tunggu user membuang sampah
        
        # --- STEP 4: AMBIL FOTO & ANALISA ---
        self.logger.info("--- [STEP 4] Menganalisa Sampah... ---")
        
        # Ambil frame terbaru (snapshot)
        snapshot_frame = self.camera.get_frame()
        
        # PENTING: Ini menggunakan method 'analyze_snapshot' yang saya sarankan sebelumnya
        # Kalau kamu belum update CameraService, method ini harus disesuaikan
        detected_label, _ = self.camera.analyze_snapshot(snapshot_frame)
        
        self.logger.info(f"[AI] Hasil Klasifikasi: {detected_label}")

        # Tentukan poin (Contoh logika sederhana)
        points = 0
        if detected_label in ['bottle', 'plastic_bottle']: # Sesuaikan nama class di YOLO kamu
            points = 10
        elif detected_label in ['cup']:
            points = 5
        
        # --- STEP 5: KIRIM KE VPS ---
        self.logger.info("--- [STEP 5] Mengirim Data... ---")
        if points > 0:
            self.api.send_transaction(
                qr_code=user_qr_data,
                total_trash=1, # Anggap 1 item per sesi
                points_earned=points
            )
        else:
            self.logger.warning("[AI] Tidak ada sampah valid terdeteksi. Data tidak dikirim.")

        # --- STEP 6: TUTUP TEMPAT SAMPAH ---
        self.logger.info("--- [STEP 6] Menutup Servo... ---")
        self.serial.send_command("CLOSE")
        
        self.logger.info("=== Sesi Selesai ===\n")

    def stop(self):
        self.camera.release()
        self.logger.info("[SYSTEM] Shutdown berhasil.")

if __name__ == "__main__":
    app = MainController()
    app.start()