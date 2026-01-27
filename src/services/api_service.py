import requests
import os
from src.utils.logger import get_logger

class ApiService:
    def __init__(self):
        self.logger = get_logger()
        self.base_url = os.getenv("VPS_API_URL")
        self.secret_key = os.getenv("API_SECRET_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "x-secret-key": self.secret_key
        }

    def send_transaction(self, qr_code, total_trash, points_earned):
        payload = {
            "qr_code": qr_code,
            "total_trash": total_trash,
            "points_earned": points_earned
        }

        self.logger.info(f"[API] Mengirim data: {payload} ke {self.base_url}")

        try:
            # Timeout 5 detik agar program tidak macet jika internet lemot
            response = requests.post(self.base_url, json=payload, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                self.logger.info("[API] Sukses! Data diterima VPS.")
                return True
            else:
                self.logger.warning(f"[API] Gagal. Respon VPS: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"[API] Error Koneksi: {e}")
            return False