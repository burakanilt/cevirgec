import logging
import os
import sys
import io

def setup_logger(log_file="cevirgec_pdf.log"):
    logger = logging.getLogger("CevirgecPDF")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console handler (safe for GUI/subthread environment where sys.stdout might be None)
    stream = sys.stdout if sys.stdout is not None else (sys.stderr if sys.stderr is not None else io.StringIO())
    ch = logging.StreamHandler(stream)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler (put in app data dir or temp)
    log_path = os.path.join(os.path.expanduser("~"), ".cevirgec_pdf", log_file)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    try:
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        pass # If we can't write to file for some reason, don't crash
    
    return logger

# Initialize once when imported
logger = setup_logger()
