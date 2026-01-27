import logging
import os
import sys

def setup_logger():
    # Buat folder logs jika belum ada
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Format log: Waktu - Level - Pesan
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    
    # Handler 1: Tulis ke File
    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(formatter)

    # Handler 2: Tulis ke Layar Terminal
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger("SmartTrash")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

def get_logger():
    return logging.getLogger("SmartTrash")