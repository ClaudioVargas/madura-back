from app.core.config import settings


class FruitModel:
    """Singleton con carga perezosa del modelo Keras.

    El modelo (TensorFlow/Keras) solo se carga en la primera llamada a ``predict``,
    evitando costos de arranque y memoria en imports. La instancia global se reutiliza
    entre peticiones.
    """

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load(self) -> None:
        # Import diferido: cargar Keras al importar el módulo arrancaría TensorFlow
        from keras.models import load_model

        self._model = load_model(settings.MODEL_PATH)

    def predict(self, image_array):
        if self._model is None:
            self._load()
        return self._model.predict(image_array)
