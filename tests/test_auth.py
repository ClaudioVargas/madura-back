"""Pruebas de salud, autenticación y rate limiting."""


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["database"] == "ok"


def test_register_y_login(client):
    r = client.post(
        "/auth/register",
        json={"nombre": "Ana", "email": "ana@test.com", "password": "secret123"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["email"] == "ana@test.com"
    assert data["rol"] == "user"
    # no se expone el hash
    assert "hashed_password" not in data

    r = client.post("/auth/token", data={"username": "ana@test.com", "password": "secret123"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["expires_in"] > 0


def test_register_email_duplicado(client):
    payload = {"nombre": "Beto", "email": "dup@test.com", "password": "secret123"}
    assert client.post("/auth/register", json=payload).status_code == 200
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 400


def test_register_password_corta(client):
    r = client.post(
        "/auth/register",
        json={"nombre": "Luis", "email": "luis@test.com", "password": "corta12"},
    )
    assert r.status_code == 422


def test_login_credenciales_invalidas(client):
    r = client.post("/auth/token", data={"username": "nadie@test.com", "password": "wrong-pass"})
    assert r.status_code == 401


def test_login_rate_limit(client):
    # 5 intentos fallidos permitidos; el 6.º debe devolver 429
    for _ in range(settings_max_attempts()):
        client.post("/auth/token", data={"username": "rata@test.com", "password": "mal12345"})
    r = client.post("/auth/token", data={"username": "rata@test.com", "password": "mal12345"})
    assert r.status_code == 429


def settings_max_attempts() -> int:
    from app.core.config import settings

    return settings.RATE_LIMIT_MAX_ATTEMPTS


def test_refresh_token(client, crear_usuario):
    crear_usuario("Carla", "carla@test.com", "secret123")
    login = client.post("/auth/token", data={"username": "carla@test.com", "password": "secret123"})
    refresh_token = login.json()["refresh_token"]

    r = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 200, r.text
    assert r.json()["access_token"]


def test_refresh_token_invalido(client):
    r = client.post("/auth/refresh", json={"refresh_token": "no-es-un-jwt"})
    assert r.status_code == 401
