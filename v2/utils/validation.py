from PIL import Image, UnidentifiedImageError
import os

def is_valid_jpeg(path: str) -> bool:
    if not os.path.isfile(path):
        return False

    try:
        with open(path, "rb") as f:
            if f.read(2) != b'\xFF\xD8':
                return False
            f.seek(-2, os.SEEK_END)
            if f.read(2) != b'\xFF\xD9':
                return False

        with Image.open(path) as img:
            img.verify()

        return True
    except (OSError, UnidentifiedImageError):
        return False
