"""Pruebas de CRUD de frutas, verduras, usuarios y permisos por rol."""


FRUTA = {"nombre": "Plátano", "color": "amarillo", "precio": 50.0, "stock": 20}
VERDURA = {"nombre": "Lechuga", "tipo": "hoja", "precio": 30.0, "stock": 15}


def test_listar_frutas_vacio(client):
    assert client.get("/frutas/").status_code == 200
    assert isinstance(client.get("/frutas/").json(), list)


def test_crear_fruta_requiere_admin(client, crear_usuario, auth_headers):
    crear_usuario("UsuarioCRUD1", "usuario@test.com", "secret123")
    headers = auth_headers("usuario@test.com", "secret123")
    r = client.post("/frutas/", json=FRUTA, headers=headers)
    assert r.status_code == 403


def test_crear_verdura_requiere_admin(client, crear_usuario, auth_headers):
    crear_usuario("UsuarioCRUD2", "usuario2@test.com", "secret123")
    headers = auth_headers("usuario2@test.com", "secret123")
    r = client.post("/verduras/", json=VERDURA, headers=headers)
    assert r.status_code == 403


def test_crud_fruta_como_admin(client, crear_usuario, auth_headers):
    crear_usuario("AdminA", "adminaa@test.com", "secret123", rol="admin")
    headers = auth_headers("adminaa@test.com", "secret123")

    r = client.post("/frutas/", json=FRUTA, headers=headers)
    assert r.status_code == 200, r.text
    fruta = r.json()
    assert fruta["nombre"] == "Plátano"
    fruta_id = fruta["id"]

    assert [f["id"] for f in client.get("/frutas/").json()] == [fruta_id]

    get = client.get(f"/frutas/{fruta_id}")
    assert get.status_code == 200
    assert get.json()["nombre"] == "Plátano"

    payload = {**FRUTA, "precio": 60.5, "stock": 10}
    r = client.put(f"/frutas/{fruta_id}", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["precio"] == 60.5
    assert r.json()["stock"] == 10

    assert client.delete(f"/frutas/{fruta_id}", headers=headers).status_code == 200
    assert client.get(f"/frutas/{fruta_id}").status_code == 404


def test_crud_verdura_como_admin(client, crear_usuario, auth_headers):
    crear_usuario("AdminV", "adminvv@test.com", "secret123", rol="admin")
    headers = auth_headers("adminvv@test.com", "secret123")

    r = client.post("/verduras/", json=VERDURA, headers=headers)
    assert r.status_code == 200, r.text
    verdura_id = r.json()["id"]

    assert [v["id"] for v in client.get("/verduras/").json()] == [verdura_id]

    payload = {**VERDURA, "precio": 33.0}
    r = client.put(f"/verduras/{verdura_id}", json=payload, headers=headers)
    assert r.status_code == 200
    assert r.json()["precio"] == 33.0

    assert client.delete(f"/verduras/{verdura_id}", headers=headers).status_code == 200
    assert client.get(f"/verduras/{verdura_id}").status_code == 404


def test_usuarios_email_duplicado(client):
    payload = {"nombre": "Uno", "email": "uuno@test.com", "password": "secret123"}
    assert client.post("/usuarios/", json=payload).status_code == 200
    r = client.post("/usuarios/", json=payload)
    assert r.status_code == 400


def test_me_autenticado(client, crear_usuario, auth_headers):
    crear_usuario("MeUser", "me@test.com", "secret123")
    headers = auth_headers("me@test.com", "secret123")
    r = client.get("/usuarios/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "me@test.com"


def test_me_sin_token(client):
    assert client.get("/usuarios/me").status_code == 401


def test_listar_usuarios_solo_admin(client, crear_usuario, auth_headers):
    crear_usuario("UserX", "userx@test.com", "secret123")
    headers_user = auth_headers("userx@test.com", "secret123")
    assert client.get("/usuarios/", headers=headers_user).status_code == 403

    crear_usuario("AdminU", "adminuu@test.com", "secret123", rol="admin")
    headers_admin = auth_headers("adminuu@test.com", "secret123")
    r = client.get("/usuarios/", headers=headers_admin)
    assert r.status_code == 200
    assert any(u["email"] == "userx@test.com" for u in r.json())


def test_actualizar_propio_usuario(client, auth_headers, crear_usuario):
    user = crear_usuario("Propio", "propio@test.com", "secret123")
    headers = auth_headers("propio@test.com", "secret123")
    r = client.put(f"/usuarios/{user.id}", json={"nombre": "Propio Actualizado"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["nombre"] == "Propio Actualizado"


def test_actualizar_usuario_ajeno_forbiden(client, auth_headers, crear_usuario):
    a = crear_usuario("AjenoA", "ajenoa@test.com", "secret123")
    crear_usuario("AjenoB", "ajenob@test.com", "secret123")
    headers_b = auth_headers("ajenob@test.com", "secret123")
    r = client.put(f"/usuarios/{a.id}", json={"nombre": "Hack"}, headers=headers_b)
    assert r.status_code == 403
