import datetime

def get_current_time() -> str:
    """Mengembalikan waktu saat ini dalam format yang mudah dibaca."""
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S pada %d %B %Y")