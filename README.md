# Madura Back

Backend para el proyecto **Madura**: una API que expone un modelo de Machine Learning (Keras/TensorFlow)
para clasificar el **estado de maduración de plátanos** (verde, madura, pasada) a partir de una foto,
junto con CRUD de frutas, verduras, usuarios y fotos, con autenticación JWT y control de roles.

| Stack | Tecnología |
| --- | --- |
| Framework | FastAPI + Uvicorn |
| ORM / BD | SQLAlchemy 2.x + SQLite |
| Validación | Pydantic v2 + pydantic-settings |
| Autenticación | JWT (python-jose, HS256) + bcrypt (hashes) |
| ML | Keras ≥ 3.15 + TensorFlow ≥ 2.21 (modelo `.keras`) |
| Procesamiento de imagen | Pillow + NumPy |
| Gestor de dependencias | `uv` |
| Migraciones | Alembic (instalado, carpeta vacía — la BD se auto-crea con `create_all`) |
| Contenedores | Docker / Docker Compose |
| Python | ≥ 3.12 (`.python-version` → 3.12; elegido por compatibilidad con TensorFlow) |

---

## Tabla de contenidos

- [Características](#características)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Configuración (variables de entorno)](#configuración-variables-de-entorno)
- [Instalación y ejecución local](#instalación-y-ejecución-local)
- [Autenticación y roles](#autenticación-y-roles)
- [Endpoints de la API](#endpoints-de-la-api)
- [Modelos de base de datos](#modelos-de-base-de-datos)
- [Modelo de Machine Learning](#modelo-de-machine-learning)
- [Docker](#docker)
- [Despliegue](#despliegue)
- [Middleware y CORS](#middleware-y-cors)

---

## Características

- 🔐 **Autenticación JWT** (`/auth/token`) y **registro de usuarios** (`/auth/register`).
- 🛡️ **Roles**: `user` (usuario normal) y `admin` (requerido para modificar frutas/verduras).
- 🍌 **Clasificación de madurez** de plátanos vía modelo Keras en `/fotos/evaluate` (subida multipart).
- 🍎 **CRUD completo** de frutas, verduras, usuarios y fotos.
- 📸 registro de **fotos** asociadas a usuarios (relación `usuarios` ↔ `fotos`).
- 🧩 **Arquitectura en capas**: `controllers` (rutas) → `services` (lógica) → `models` (ORM) + `schemas` (DTOs).
- 🐳 **Docker / Docker Compose** con persistencia del volumen de datos en `./data`.
- 📝 **Middleware de logging** de peticiones (método, ruta, estado y tiempo de respuesta).
- 🌐 **CORS** configurado para el frontend Angular local y desplegado en Render.
- 🌱 La base de datos se inicializa automáticamente al arrancar (`Base.metadata.create_all`).

---

## Estructura del proyecto

```
madura_back/
├── main.py                     # Punto de entrada: app FastAPI, lifespan, CORS, handlers, routers
├── pyproject.toml              # Definición del proyecto, dependencias y tooling (uv, ruff, pytest)
├── uv.lock                     # Lockfile generado por uv (incluye grupo dev)
├── Dockerfile                  # Imagen python:3.13-slim + uv (sin dependencias dev)
├── docker-compose.yml          # Orquestación local con volumen ./data
├── .python-version             # 3.12
├── .env.example                # Plantilla de variables de entorno (copiar a .env)
├── .gitignore / .dockerignore
├── database.db                 # SQLite local generada al ejecutar sin Docker
├── app/
│   ├── __init__.py
│   ├── controllers/            # Routers FastAPI (endpoints)
│   │   ├── auth.py                 # /auth/token, /auth/register, /auth/refresh + rate limit
│   │   ├── users.py                # /usuarios/*
│   │   ├── frutas.py               # /frutas/*
│   │   ├── verduras.py             # /verduras/*
│   │   └── fotos.py                # /fotos/* (incluye /fotos/evaluate protegido)
│   ├── core/
│   │   └── config.py            # Settings (pydantic-settings, lee .env)
│   ├── database/
│   │   └── base.py              # Engine, SessionLocal, Base, init_db() y PRAGMA foreign_keys
│   ├── middleware/
│   │   └── logging.py           # RequestLoggingMiddleware (logging, no print)
│   ├── models/                  # Modelos SQLAlchemy + modelo Keras
│   │   ├── user.py              #   Usuario
│   │   ├── photo.py             #   Foto
│   │   ├── fruta.py             #   Fruta
│   │   ├── verdura.py           #   Verdura
│   │   ├── fruit_model.py       #   Wrapper SINGLETON con carga perezosa del modelo
│   │   └── modelo_platano.keras #   Modelo entrenado (~11 MB, no versionado)
│   ├── schemas/                 # Schemas Pydantic v2 (from_attributes=True)
│   │   ├── user.py              #   UsuarioCreate / UsuarioOut / UsuarioUpdate
│   │   ├── token.py             #   Token / RefreshRequest / TokenData
│   │   ├── fruta.py             #   FrutaCreate / FrutaOut
│   │   ├── verdura.py           #   VerduraCreate / VerduraOut
│   │   └── photo.py             #   FotoCreate / FotoOut
│   ├── security/
│   │   ├── jwt.py               # Crear/decodificar tokens JWT (access y refresh)
│   │   ├── deps.py              # get_db, get_current_user, require_role()
│   │   └── rate_limit.py        # LoginRateLimiter (intentos fallidos de login por IP)
│   ├── services/                # Lógica de negocio
│   │   ├── user_service.py      #   Hash bcrypt, crear/actualizar/consultar usuarios
│   │   ├── fruta_service.py     #   CRUD frutas + evaluate_fruit()
│   │   ├── verdura_service.py   #   CRUD verduras
│   │   └── photo_service.py     #   CRUD fotos
│   └── utils/
│       └── image_utils.py       # preprocess_image(): RGB → 244x244 → /255 (con límite 5 MB)
├── data/
│   └── madura.db                # SQLite persistida por Docker (volumen ./data)
├── alembic/                     # Carpeta vacía (Alembic instalado pero sin usar)
└── tests/                       # Suite pytest (auth, CRUD, fotos) + conftest
```

---

## Configuración (variables de entorno)

La configuración se lee de un archivo `.env` (plantilla en `.env.example`) o de variables de
entorno mediante `pydantic-settings` (`app/core/config.py`).

| Variable | Default | Descripción |
| --- | --- | --- |
| `PROJECT_NAME` | `madura_back` | Nombre del proyecto |
| `MODEL_PATH` | `app/models/modelo_platano.keras` | Ruta del modelo Keras |
| `DATABASE_URL` | `sqlite:///database.db` | URL de la BD (el Docker la sobreescribe con `sqlite:////data/madura.db`) |
| `SECRET_KEY` | `dev-secret-change-me-in-production` | ⚠️ Clave JWT. **Debe cambiarse en producción**. |
| `ALGORITHM` | `HS256` | Algoritmo de firma JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (1 día) | Duración del token de acceso |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | `10080` (7 días) | Duración del refresh token |
| `CORS_ORIGINS` | `http://localhost:4200,http://127.0.0.1:4200,https://madura-front.onrender.com` | Orígenes CORS separados por comas |
| `RATE_LIMIT_MAX_ATTEMPTS` | `5` | Intentos fallidos de login permitidos por IP |
| `RATE_LIMIT_WINDOW_SECONDS` | `900` | Ventana del rate limiter (15 min) |

> El archivo `.env` está en `.gitignore`. La plantilla de referencia es `.env.example`.

---

## Instalación y ejecución local

> El proyecto usa **`uv`** como gestor de dependencias (define `pyproject.toml` + `uv.lock`).
> En versiones anteriores el README sugería `pip install -r requirements.txt` (ese archivo no existe).
> Requiere **Python ≥ 3.12**.

```bash
# 1. Crear y activar el entorno virtual
python -m venv .venv
.\.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # Linux/macOS

# 2. Sincronizar dependencias (incluye el grupo dev: pytest, httpx, ruff)
uv sync --dev

# 3. Ejecutar el servidor de desarrollo
uv run uvicorn main:app --reload --port 8000
```

La app arranca con:

- **Health checks:** `GET /` → `{"status": "ok", "message": "Backend running successfully"}` y `GET /health` (verifica la BD).
- **Documentación interactiva OpenAPI:** http://localhost:8000/docs
- **Redoc:** http://localhost:8000/redoc

Lint y tests:

```bash
uv run ruff check app tests main.py   # lint (config en pyproject.toml)
uv run pytest                         # 28 pruebas con BD temporal
```

> 🟢 El modelo Keras ahora usa **carga perezosa** (`FruitModel` en `app/models/fruit_model.py`):
> se instancia al importar, pero TensorFlow solo se carga en la **primera** llamada a `/fotos/evaluate`.
> El arranque de la API ya no depende de cargar el modelo.

---

## Autenticación y roles

### Flujo de autenticación

1. **Registro:** `POST /auth/register` con `{nombre, email, password}` (mín. **8 caracteres**).
   La contraseña se guarda **hasheada con bcrypt** (`app/services/user_service.py`).
   El rol por defecto es `user`.
2. **Login:** `POST /auth/token` usando el esquema `OAuth2PasswordRequestForm`
   (`username` = email, `password` = contraseña).
   Devuelve `{access_token, token_type, expires_in, refresh_token}`.
   - El login cuenta con **rate limiting**: tras 5 intentos fallidos por IP se responde `429`
     durante 15 minutos (`RATE_LIMIT_MAX_ATTEMPTS` / `RATE_LIMIT_WINDOW_SECONDS`, en memoria).
3. **Uso:** enviar el token de acceso en el header `Authorization: Bearer <token>`.
   Cuando expire, **renovarlo** con `POST /auth/refresh` enviando `{"refresh_token": "..."}`.

### Roles

| Rol | Permisos |
| --- | --- |
| `user` | Evaluar frutas, crear/eliminar sus fotos, ver y editar su propio usuario |
| `admin` | Todo lo anterior + CRUD de frutas y verduras; listar usuarios; borrar fotos ajenas |

- El **token de acceso** expira en `ACCESS_TOKEN_EXPIRE_MINUTES` (24 h por defecto, configurable).
- El **refresh token** expira en `REFRESH_TOKEN_EXPIRE_MINUTES` (7 días, configurable) y solo es
  válido en `/auth/refresh` (los endpoints protegidos rechazan tokens de tipo `refresh`).
- La dependencia `require_role()` permite `admin` siempre (aunque se pida rol `user`).
- Solo el **dueño del recurso** o un `admin` pueden borrar una foto; en `POST /fotos/` el
  `usuario_id` del payload se ignora para usuarios normales (se usa el del token).

> 🔒 **Nota de seguridad:** `SECRET_KEY` tiene un **valor por defecto de desarrollo** en
> `app/core/config.py`. En producción **debe definirse** mediante variable de entorno
> (ver `.env.example`); de lo contrario cualquiera podría falsificar tokens.

---

## Endpoints de la API

### Salud del sistema

| Método | Ruta | Protegido | Descripción |
| --- | --- | --- | --- |
| `GET` | `/` | no | Health check básico |
| `GET` | `/health` | no | Health check con verificación de la BD (`503` si la BD falla) |

### Autenticación (`prefix = /auth`)

| Método | Ruta | Protegido | Descripción |
| --- | --- | --- | --- |
| `POST` | `/auth/token` | no | Login (form `username`=email, `password`) → `Token` (con rate limiting) |
| `POST` | `/auth/register` | no | Registro de usuario → `UsuarioOut` |
| `POST` | `/auth/refresh` | no | Renueva el `access_token` con un `refresh_token` válido |

### Usuarios (`prefix = /usuarios`)

| Método | Ruta | Protegido | Descripción |
| --- | --- | --- | --- |
| `POST` | `/usuarios/` | no | Crear usuario (valida email duplicado) |
| `GET` | `/usuarios/` | **admin** | Listar usuarios (paginado: `?skip=&limit=`) |
| `GET` | `/usuarios/me` | **autenticado** | Datos del usuario actual |
| `PUT` | `/usuarios/{user_id}` | autenticado (self o admin) | Actualizar nombre/email/password/rol |

### Frutas (`prefix = /frutas`)

| Método | Ruta | Protegido | Descripción |
| --- | --- | --- | --- |
| `GET` | `/frutas/` | no | Listar frutas (paginado) |
| `POST` | `/frutas/` | **admin** | Crear fruta (guarda `creador_id`) |
| `GET` | `/frutas/{fruta_id}` | no | Obtener una fruta |
| `PUT` | `/frutas/{fruta_id}` | **admin** | Actualizar fruta |
| `DELETE` | `/frutas/{fruta_id}` | **admin** | Eliminar fruta |

### Verduras (`prefix = /verduras`)

| Método | Ruta | Protegido | Descripción |
| --- | --- | --- | --- |
| `GET` | `/verduras/` | no | Listar verduras (paginado) |
| `POST` | `/verduras/` | **admin** | Crear verdura (guarda `creador_id`) |
| `GET` | `/verduras/{verdura_id}` | no | Obtener una verdura |
| `PUT` | `/verduras/{verdura_id}` | **admin** | Actualizar verdura |
| `DELETE` | `/verduras/{verdura_id}` | **admin** | Eliminar verdura |

### Fotos y evaluación del modelo (`prefix = /fotos`)

| Método | Ruta | Protegido | Descripción |
| --- | --- | --- | --- |
| `POST` | `/fotos/evaluate` | **autenticado** | Subir imagen (multipart `file`) → `{"estado": "verde" \| "madura" \| "pasada" \| "desconocido"}`. Tamaño máx. 5 MB; `400` si no es imagen; `413` si excede el tamaño |
| `GET` | `/fotos/` | no | Listar fotos (paginado) |
| `POST` | `/fotos/` | **user/admin** | Registrar una foto. Usuario normal: se asigna su `id` aunque envie `usuario_id` |
| `GET` | `/fotos/{foto_id}` | no | Obtener una foto |
| `DELETE` | `/fotos/{foto_id}` | **user/admin** | Eliminar una foto (solo el dueño o admin) |

### Schemas de entrada (resumen)

- `UsuarioCreate`: `{nombre: str, email: EmailStr, password: str (mín 8)}`
- `UsuarioUpdate`: `{nombre?, email?, password?, rol?}` (todos opcionales)
- `FrutaCreate` / `VerduraCreate`: `{nombre, color|tipo?, precio (>0), stock (>0, entero)}`
- `FotoCreate`: `{url: HttpUrl, usuario_id?: int}`
- `Token`: `{access_token, token_type="bearer", expires_in, refresh_token?}`

---

## Modelos de base de datos

La BD se crea automáticamente al iniciar (`init_db()` → `Base.metadata.create_all`).
Tablas definidas en `app/models/`:

| Tabla | Columnas |
| --- | --- |
| `usuarios` | `id` (PK), `nombre`, `email` (único, indexado), `hashed_password` (255), `rol` (default `user`) |
| `fotos` | `id` (PK), `url`, `usuario_id` (FK → `usuarios.id`) |
| `frutas` | `id` (PK), `nombre`, `color`, `precio` (float, default 0), `stock` (int, default 0), `creador_id` |
| `verduras` | `id` (PK), `nombre`, `tipo`, `precio` (float, default 0), `stock` (int, default 0), `creador_id` |

- Relación: `Usuario` 1—N `Foto` (con `cascade="all, delete-orphan"`).
- Local sin Docker: se crea `database.db` en la raíz.
- Con Docker: se usa `/data/madura.db` (volumen `./data` del host).

> **Alembic** está instalado y existe la carpeta `alembic/`, pero está **vacía y sin configurar**:
> no hay `alembic.ini`, ni `env.py`, ni `versions/`. Los cambios de esquema actualmente se resuelven
> eliminando/regenerando la BD con `create_all`.

---

## Modelo de Machine Learning

- **Archivo:** `app/models/modelo_platano.keras` (~11 MB, excluido del repo por `.gitignore`).
- **Carga:** `app/models/fruit_model.py` → `FruitModel` (singleton) con **carga perezosa**: el modelo se
  instancia al importar, pero TensorFlow/Keras solo se cargan en la **primera predicción**.
- **Límite de subida:** 5 MB por imagen (`MAX_IMAGE_BYTES` en `app/utils/image_utils.py`).
- **Preprocesado** (`app/utils/image_utils.py`):
  1. `Image.open(...).convert("RGB")`
  2. `resize((244, 244))`
  3. `np.array(img) / 255.0`
  4. `np.expand_dims(..., axis=0)` (batch de 1)
- **Salida (3 clases):** `0 → "verde"`, `1 → "madura"`, `2 → "pasada"`; cualquier otro índice → `"desconocido"`.

```python
# Ejemplo de uso directo
from app.services.fruta_service import evaluate_fruit
resultado = evaluate_fruit(open("platanos.jpg", "rb"))
print(resultado)  # verde | madura | pasada
```

---

## Docker

### Dockerfile

- Base `python:3.13-slim`, instala `uv`, copia `pyproject.toml` + `uv.lock` primero (cachea capas),
  ejecuta `uv sync --frozen --no-dev` (sin dependencias de desarrollo) y después copia el código fuente.
- Expone el puerto `8000` y lanza `uv run uvicorn main:app --host 0.0.0.0 --port 8000`.
- Define `DATABASE_URL=sqlite:////data/madura.db`.
- ⚠️ **El modelo `.keras` no está versionado** (`.gitignore`): asegúrate de que
  `app/models/modelo_platano.keras` exista antes de `docker build`, o la predicción fallará.

### docker-compose.yml

| Campo | Valor |
| --- | --- |
| Imagen | `srdarus/madura_back:v1` |
| Puerto | `8000:8000` |
| Variable | `DATABASE_URL=sqlite:////data/madura.db` |
| Volumen | `./data:/data` (persistencia SQLite) |
| Reinicio | `unless-stopped` |

### Comandos

```bash
docker compose build                  # construir la imagen
docker compose up -d                  # levantar el contenedor
docker push srdarus/madura_back:v1    # ejemplo para subir la imagen a Docker Hub
```

- App: http://localhost:8000
- Docs: http://localhost:8000/docs
- La base de datos SQLite persiste en `./data/madura.db`.

---

## Despliegue

- El `GET /` (health check) se añadió expresamente para solucionar el **404 en Render**
  (la plataforma verifica la raíz de la app). Además existe `GET /health` que verifica la BD.
- **CORS** se configura vía `CORS_ORIGINS` (entorno) y por defecto permite el frontend:
  - `http://localhost:4200` y `http://127.0.0.1:4200` (Angular local)
  - `https://madura-front.onrender.com` (frontend desplegado)
- ⚠️ **Variables obligatorias en producción:** `SECRET_KEY` (clave JWT única). Recomendadas:
  `CORS_ORIGINS`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `DATABASE_URL`.
- ⚠️ **`/fotos/evaluate` ahora requiere autenticación**: el frontend debe enviar
  `Authorization: Bearer <token>` (usar `/auth/refresh` antes de que expire el token de acceso).
- Requisito de memoria: la primera llamada a `/fotos/evaluate` carga TensorFlow/Keras en memoria;
  el despliegue debe tener RAM suficiente para el modelo.

---

## Middleware y CORS

- `RequestLoggingMiddleware` (`app/middleware/logging.py`): registra con el módulo `logging`
  `MÉTODO ruta - status - tiempo_ms` por cada petición.
- `CORSMiddleware` (`main.py`): `allow_credentials=True`,
  `allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]`, `allow_headers=["*"]`
  para los orígenes de `CORS_ORIGINS`.

---

## Notas, pendientes y observaciones

### ✅ Cambios aplicados en esta revisión

- **Seguridad**:
  - `SECRET_KEY` movida a `Settings`/`.env` (creada `.env.example`).
  - Eliminados los `print()` que exponían contraseñas y otros prints de depuración.
  - `/fotos/evaluate` protegido (requiere token); `/fotos/` y su DELETE validan propiedad.
  - Rate limiting de login (5 intentos por IP cada 15 min).
  - Contraseñas con mínimo **8 caracteres**.
  - `PRAGMA foreign_keys=ON` activado en SQLite.
  - CORS centralizado y configurable por entorno.
- **Manejo de errores**:
  - Sesiones de BD ya no se fugan en `/auth/*` (usos de `Depends(get_db)`).
  - `/fotos/evaluate` devuelve `400` (no imagen), `413` (mayor a 5 MB) en lugar de 500.
  - Handlers globales JSON para `422`, `IntegrityError → 409` y `Exception → 500`.
  - Duplicados de email validados desde la capa de controlador.
- **Arquitectura/calidad**:
  - Modelo Keras con **carga perezosa** (singleton) — arranque rápido sin TensorFlow.
  - Actualización de usuario movida al servicio; eliminado `.dict()` deprecado → `model_dump()`.
  - Paginación (`skip`/`limit`) expuesta en listados; resultados ordenados por `id`.
  - Registro de logs con `logging` (no `print`); `/health` nuevo.
  - `ruff` (lint) y `pytest` configurados; **28 pruebas** en `tests/`; lockfile actualizado.
  - `docker-compose`/Dockerfile usa `uv sync --frozen --no-dev`.

### ⚠️ Observaciones importantes (pendiente / decisión)

1. **`SECRET_KEY`**: el default `dev-secret-change-me-in-production` es solo para desarrollo.
   Definir `SECRET_KEY` en producción (Render env var) y **rotarla** si fue usada antes.
2. **Cambios que rompen contratos con el frontend**:
   - `/fotos/evaluate` ahora exige `Authorization: Bearer <token>` (antes era público).
   - Las contraseñas de registro/actualización exigen mínimo 8 caracteres (antes 6).
   - La respuesta de login incluye ahora `refresh_token` (campo nuevo, aditivo).
3. **Versión de Python**: local `.python-version` = **3.12** (por TensorFlow), mientras que el
   `Dockerfile` usa **python:3.13-slim**. Alinear el Dockerfile a 3.12 o verificar 3.13 expuesto.
4. **Modelo no versionado**: `*.keras` está en `.gitignore`. El Dockerfile no lo descarga:
   debe existir en la copia de build o montarse por volumen.
5. **Rate limiter en memoria**: válido para un solo proceso. En multi-instancia se necesita
   Redis o límites en el reverse proxy (nginx).
6. **Alembic**: instalado pero sin configurar; la BD sigue auto-creándose con `create_all`.
   Si el esquema evoluciona, configurar migraciones.
7. **CI/CD**: hay suite de tests y ruff, pero no hay GitHub Actions ni despliegue automatizado.
8. **`respaldo.mejoras.md`**: archivo en la raíz con el listado original de mejoras;
   se puede eliminar o conservar como referencia.

### 🟢 Ideas a futuro (no críticas)

- Script para crear el primer usuario `admin` (bootstrap).
- Timestamps `created_at`/`updated_at` y tabla de auditoría.
- Endpoint batch de evaluación (`/fotos/evaluate` por lote).
- Request-ID en el middleware y correlación de logs.
- Métricas (Prometheus `/metrics`) o reporte de errores (Sentry).
- `GET /usuarios/{id}` (hoy solo existe `me` y el listado admin).