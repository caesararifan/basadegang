import serial
import time
import os
from src.utils.logger import get_logger

class SerialService:
    def __init__(self):
        self.logger = get_logger()
        self.port = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
        self.baud = int(os.getenv("BAUD_RATE", 9600))
        self.connection = None
        self.connect()

    def connect(self):
        try:
            self.connection = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2) # Wajib tunggu Arduino reset saat konek
            self.logger.info(f"[HARDWARE] Terhubung ke ESP32 di {self.port}")
        except Exception as e:
            self.logger.error(f"[HARDWARE] Gagal konek ke ESP32: {e}")
            self.connection = None

    def send_command(self, command):
        """Kirim perintah: OPEN atau CLOSE"""
        if self.connection:
            try:
                msg = f"{command}\n"
                self.connection.write(msg.encode('utf-8'))
                self.logger.info(f"[SERIAL] Sent: {command}")
                return True
            except Exception as e:
                self.logger.error(f"[SERIAL] Error write: {e}")
                # Coba reconnect jika putus
                self.connect()
                return False
        else:
            self.logger.warning(f"[SIMULASI] Hardware tidak ada. Perintah '{command}' diabaikan.")
            return True