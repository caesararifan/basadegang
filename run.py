import os

# --- BARIS SAKTI ANTI ERROR OMP ---
# Ini harus ditaruh paling atas sebelum import library lain
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# ----------------------------------

from dotenv import load_dotenv
from src.main_controller import MainController
from src.utils.logger import setup_logger

# 1. Load Environment Variables
load_dotenv()

# 2. Setup Logging
logger = setup_logger()

# 3. Jalankan Aplikasi
if __name__ == "__main__":
    try:
        app = MainController()
        app.run()
    except KeyboardInterrupt:
        logger.info("Aplikasi dimatikan User.")
    except Exception as e:
        logger.critical(f"App Crash: {e}", exc_info=True)