import time
from collections import defaultdict
from threading import Lock


class LoginRateLimiter:
    """Limita intentos fallidos de login por IP (en memoria, válido en single-process).

    Para despliegues multi-instancia se recomienda un almacén compartido
    (Redis) o el uso de un proxy/reverse proxy con límites nativos.
    """

    def __init__(self, max_attempts: int, window_seconds: int) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def is_blocked(self, key: str) -> bool:
        """True si la clave ya superó los intentos permitidos dentro de la ventana."""
        with self._lock:
            now = time.time()
            recent = [ts for ts in self._attempts[key] if now - ts <= self.window_seconds]
            self._attempts[key] = recent
            return len(recent) >= self.max_attempts

    def record_failure(self, key: str) -> None:
        """Registra un intento fallido para la clave dada."""
        with self._lock:
            self._attempts[key].append(time.time())

    def reset(self, key: str) -> None:
        """Limpia los intentos registrados para una clave (p. ej. tras login exitoso)."""
        with self._lock:
            self._attempts.pop(key, None)

    def reset_all(self) -> None:
        """Limpia todos los intentos (útil en tests)."""
        with self._lock:
            self._attempts.clear()
