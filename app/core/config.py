from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fruit State API"
    MODEL_PATH: str = "app/models/modelo_platano.keras"

settings = Settings()
