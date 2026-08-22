import time
from functools import wraps
import logging

def time_it(action_name="İşlem"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                logging.getLogger("CevirgecPDF").info(f"[{action_name}] tamamlandı: {elapsed:.3f} saniye")
        return wrapper
    return decorator
