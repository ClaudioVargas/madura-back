from PIL import Image
import numpy as np

def preprocess_image(image_file):
    img = Image.open(image_file).convert("RGB")
    img = img.resize((244, 244))  # tamaño esperado por el modelo
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)
