FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=sqlite:////data/madura.db

RUN pip install --no-cache-dir uv

# 1. Copia ÚNICAMENTE los archivos de dependencias
COPY pyproject.toml uv.lock ./

# 2. Crea la carpeta de datos e instala las librerías PRIMERO
#    (--no-dev: no se instalan pytest/ruff/httpx en la imagen de producción)
RUN mkdir -p /data
RUN uv sync --frozen --no-dev

# 3. Copia tu código fuente AL FINAL (Esto es lo que cambia seguido)
COPY main.py ./
COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
