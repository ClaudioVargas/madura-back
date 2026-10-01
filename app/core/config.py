from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central de la aplicación.

    Se lee desde variables de entorno y/o un archivo ``.env``.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Proyecto
    PROJECT_NAME: str = "madura_back"

    # Modelo de Machine Learning
    MODEL_PATH: str = "app/models/modelo_platano.keras"

    # Base de datos
    DATABASE_URL: str = "sqlite:///database.db"

    # Seguridad JWT (en producción, SECRET_KEY debe venir de una variable de entorno)
    SECRET_KEY: str = "dev-secret-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 día
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días

    # Orígenes CORS permitidos (separados por comas)
    CORS_ORIGINS: str = (
        "http://localhost:4200,"
        "http://127.0.0.1:4200,"
        "https://madura-front.onrender.com"
    )

    # Rate limiting de login (intentos fallidos por IP)
    RATE_LIMIT_MAX_ATTEMPTS: int = 5
    RATE_LIMIT_WINDOW_SECONDS: int = 900  # 15 minutos

    @property
    def cors_origins_list(self) -> list[str]:
        """Devuelve los orígenes CORS como lista, ignorando entradas vacías."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
