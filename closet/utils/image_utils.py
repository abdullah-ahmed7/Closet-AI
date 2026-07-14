"""
Handles saving uploaded images to disk with a unique filename.
"""
import uuid
from pathlib import Path
from PIL import Image

IMAGES_DIR = Path(__file__).resolve().parent.parent / "data" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_image(uploaded_file, max_dim=800):
    """
    Saves a Streamlit UploadedFile to disk, resized so files stay small.
    Returns the saved file's path as a string.
    """
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((max_dim, max_dim))

    filename = f"{uuid.uuid4().hex}.jpg"
    save_path = IMAGES_DIR / filename
    img.save(save_path, "JPEG", quality=85)

    return str(save_path)
