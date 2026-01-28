import os

# --- BARIS SAKTI ANTI ERROR OMP ---
# Bagus ini tetap dipertahankan, terutama kalau pakai library AI di beberapa environment
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# ----------------------------------

from dotenv import load_dotenv
from src.main_controller import MainController
# Pastikan import ini sesuai dengan file utils/logger.py kamu
# Kalau di file lain pakai get_logger, sesuaikan saja.
from src.utils.logger import get_logger 

# 1. Load Environment Variables
load_dotenv()

# 2. Setup Logging (Opsional di sini, karena di dalam MainController sudah ada logger juga)
# Tapi oke kalau mau log level global aplikasi
logger = get_logger()

# 3. Jalankan Aplikasi
if __name__ == "__main__":
    try:
        app = MainController()
        logger.info("Memulai Aplikasi Deteksi Sampah...")
        
        # PERBAIKAN DI SINI:
        app.start() 
        
    except KeyboardInterrupt:
        logger.info("Aplikasi dimatikan User.")
    except Exception as e:
        logger.critical(f"App Crash: {e}", exc_info=True)