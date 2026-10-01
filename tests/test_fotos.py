"""Pruebas de fotos: evaluación con modelo mockeado, validación y propiedad."""

import io

import numpy as np
from PIL import Image


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (100, 100), (120, 30, 200)).save(buf, format="PNG")
    return buf.getvalue()


def _foto_payload():
    return {"url": "https://example.com/foto-test.jpg"}


def test_evaluate_requiere_auth(client):
    r = client.post("/fotos/evaluate", files={"file": ("a.png", _png_bytes(), "image/png")})
    assert r.status_code in (401, 403)


def test_evaluate_archivo_invalido(client, crear_usuario, auth_headers):
    crear_usuario("EvaTxt", "evatxt@test.com", "secret123")
    headers = auth_headers("evatxt@test.com", "secret123")
    r = client.post(
        "/fotos/evaluate",
        files={"file": ("a.txt", b"no soy una imagen", "text/plain")},
        headers=headers,
    )
    assert r.status_code == 400


def test_evaluate_ok(client, crear_usuario, auth_headers, monkeypatch):
    crear_usuario("EvaPng", "evapng@test.com", "secret123")
    headers = auth_headers("evapng@test.com", "secret123")

    class FakeModel:
        def predict(self, array):
            return np.array([[0.1, 0.8, 0.1]])  # índice 1 -> "madura"

    monkeypatch.setattr("app.services.fruta_service.fruit_model", FakeModel())

    r = client.post("/fotos/evaluate", files={"file": ("a.png", _png_bytes(), "image/png")}, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["estado"] == "madura"


def test_crear_foto_sin_auth(client):
    r = client.post("/fotos/", json=_foto_payload())
    assert r.status_code in (401, 403)


def test_foto_asignada_al_usuario_autenticado(client, crear_usuario, auth_headers):
    dueno = crear_usuario("FDueno", "fdueno@test.com", "secret123")
    headers = auth_headers("fdueno@test.com", "secret123")

    # El payload no envía usuario_id: se asigna el del usuario autenticado
    r = client.post("/fotos/", json=_foto_payload(), headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["usuario_id"] == dueno.id


def test_foto_solo_la_borra_su_dueno(client, crear_usuario, auth_headers):
    dueno = crear_usuario("FDueno2", "fdueno2@test.com", "secret123")
    crear_usuario("FOtro", "fotro@test.com", "secret123")
    headers_dueno = auth_headers("fdueno2@test.com", "secret123")
    headers_otro = auth_headers("fotro@test.com", "secret123")

    r = client.post("/fotos/", json=_foto_payload(), headers=headers_dueno)
    assert r.status_code == 200, r.text
    foto_id = r.json()["id"]
    assert r.json()["usuario_id"] == dueno.id

    # El otro usuario no puede borrarla
    assert client.delete(f"/fotos/{foto_id}", headers=headers_otro).status_code == 403

    # El dueño sí
    assert client.delete(f"/fotos/{foto_id}", headers=headers_dueno).status_code == 200
    assert client.get(f"/fotos/{foto_id}").status_code == 404


def test_admin_puede_borrar_cualquier_foto(client, crear_usuario, auth_headers):
    crear_usuario("FUser", "fuser@test.com", "secret123")
    headers_user = auth_headers("fuser@test.com", "secret123")

    r = client.post("/fotos/", json=_foto_payload(), headers=headers_user)
    assert r.status_code == 200, r.text
    foto_id = r.json()["id"]

    crear_usuario("FAdmin", "fadmin@test.com", "secret123", rol="admin")
    headers_admin = auth_headers("fadmin@test.com", "secret123")

    assert client.delete(f"/fotos/{foto_id}", headers=headers_admin).status_code == 200


def test_paginacion_fotos(client, crear_usuario, auth_headers):
    crear_usuario("Xfotos", "xfotos@test.com", "secret123")
    headers = auth_headers("xfotos@test.com", "secret123")
    for i in range(5):
        r = client.post("/fotos/", json={"url": f"https://example.com/f{i}.jpg"}, headers=headers)
        assert r.status_code == 200
    r = client.get("/fotos/?skip=0&limit=3")
    assert r.status_code == 200
    assert len(r.json()) == 3
