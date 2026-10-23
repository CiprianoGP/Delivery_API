import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def criar_usuario_teste():
    email = f"{uuid.uuid4().hex[:8]}@teste.com"
    dados = {"nome": "Teste", "email": email, "senha": "123456"}
    resposta = client.post("/auth/criar_conta", json=dados)
    return dados, resposta


def test_criar_conta():
    _, resposta = criar_usuario_teste()
    assert resposta.status_code == 200


def test_email_duplicado():
    dados, _ = criar_usuario_teste()
    resposta = client.post("/auth/criar_conta", json=dados)
    assert resposta.status_code == 400


def test_login_correto():
    dados, _ = criar_usuario_teste()
    resposta = client.post("/auth/login", json={"email": dados["email"], "senha": dados["senha"]})
    assert resposta.status_code == 200
    assert "access_token" in resposta.json()


def test_login_senha_errada():
    dados, _ = criar_usuario_teste()
    resposta = client.post("/auth/login", json={"email": dados["email"], "senha": "errada"})
    assert resposta.status_code == 400


def test_refresh_token_valido():
    dados, _ = criar_usuario_teste()
    login = client.post("/auth/login", json={"email": dados["email"], "senha": dados["senha"]}).json()
    headers = {"Authorization": f"Bearer {login['refresh_token']}"}
    resposta = client.get("/auth/refresh", headers=headers)
    assert resposta.status_code == 200


def test_refresh_token_invalido():
    headers = {"Authorization": "Bearer abc"}
    resposta = client.get("/auth/refresh", headers=headers)
    assert resposta.status_code == 401