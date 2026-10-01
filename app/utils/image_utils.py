import io

import numpy as np
from PIL import Image

IMAGE_SIZE = (244, 244)
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


class ImageTooLargeError(ValueError):
    """Se lanza cuando la imagen supera el tamaño máximo permitido."""


def preprocess_image(image_file, max_bytes: int = MAX_IMAGE_BYTES) -> np.ndarray:
    """Lee, valida y normaliza una imagen para el modelo.

    1. Lee como máximo ``max_bytes`` (evita agotar memoria con archivos gigantes).
    2. Convierte a RGB y redimensiona a 244x244 (tamaño esperado por el modelo).
    3. Normaliza a [0, 1] y agrega la dimensión de batch.

    Lanza ``ImageTooLargeError`` si el archivo supera el tamaño máximo y
    ``PIL.UnidentifiedImageError`` si no es una imagen válida.
    """
    data = image_file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ImageTooLargeError(
            f"La imagen supera el tamaño máximo permitido de {max_bytes} bytes"
        )

    img = Image.open(io.BytesIO(data)).convert("RGB")
    img = img.resize(IMAGE_SIZE)
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)
