import cv2
from src.utils.logger import get_logger

class QrService:
    def __init__(self):
        self.logger = get_logger()
        self.detector = cv2.QRCodeDetector()

    def scan(self, frame):
        """
        Mengembalikan string data QR jika ditemukan, atau None jika tidak.
        """
        try:
            data, bbox, _ = self.detector.detectAndDecode(frame)
            if data:
                return data
        except Exception as e:
            pass # Error decoding biasa terjadi kalau QR miring/buram
        return None