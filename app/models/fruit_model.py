from keras.models import load_model
import keras  # Importamos keras para acceder a la clase Model
from app.core.config import settings

class FruitModel:
    # Indicamos al editor que self.model será un objeto de tipo keras.Model
    model: keras.Model
    def __init__(self):
        self.model = load_model(settings.MODEL_PATH)

    def predict(self, image_array):
        prediction = self.model.predict(image_array)
        return prediction
