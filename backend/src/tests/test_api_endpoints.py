# backend/src/tests/test_api_endpoints.py
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.src.main import app
# Importar get_db para fazer o override da sessão de banco de dados
from backend.src.database import get_db 
from backend.src.utils.security import get_current_user, get_current_admin_user

# =========================
# Mock de Usuário
# =========================
class MockUser:
    def __init__(self, id, email, password="hashed", funds=100.0, role="user"):
        self.id = id
        self.email = email
        self.password = password
        self.funds = funds
        self.role = role
        self.sub = email 

    def __getitem__(self, item):
        if item == 'sub': return self.email
        if item == 'role': return self.role
        return getattr(self, item)

# =========================
# Overrides de Dependências
# =========================
def override_get_current_user():
    return MockUser(5, "user@example.com")

def override_get_current_admin():
    return MockUser(1, "admin@example.com", role="admin")

# NOVO: Mock da Sessão de Base de Dados
# Isto impede que o código tente fazer commit/refresh reais em objetos Mock
def override_get_db():
    mock_db = MagicMock()
    mock_db.refresh.return_value = None # Impede erro no db.refresh(user)
    mock_db.commit.return_value = None  # Impede erro no db.commit()
    return mock_db

app.dependency_overrides = {
    get_current_user: override_get_current_user,
    get_current_admin_user: override_get_current_admin,
    get_db: override_get_db  # <--- ADICIONADO
}

client = TestClient(app)

# =========================
# Testes Registro
# =========================
@patch("backend.src.utils.validation_utils.hash_password", return_value="hashed_password")
@patch("backend.src.database.DatabaseService.create_user", return_value="101")
def test_register_user_success(mock_create_user, mock_hash_password):
    response = client.post("/register_user", json={
        "name": "New User",
        "email": "new@test.com",
        "password": "Password123!",
        "role": "user",
        "funds": 0.0
    })
    assert response.status_code == 201
    assert response.json()["user_id"] == "101"

@patch("backend.src.utils.validation_utils.hash_password", return_value="hashed_password")
@patch("backend.src.database.DatabaseService.create_user", side_effect=Exception("DB Error"))
def test_register_user_fail(mock_create_user, mock_hash_password):
    response = client.post("/register_user", json={
        "name": "New User",
        "email": "fail@test.com",
        "password": "Password123!",
        "role": "user",
        "funds": 0.0
    })
    assert response.status_code == 500

# =========================
# Testes Login
# =========================
@patch("backend.src.main.verify_password", return_value=True)
@patch("backend.src.utils.auth_utils.create_access_token", return_value="mock_access_token")
@patch("backend.src.database.DatabaseService.get_user_by_email", return_value=MockUser(5, "login@test.com"))
def test_login_success(mock_get_user, mock_create_token, mock_verify_password):
    response = client.post("/login", json={"email": "login@test.com", "password": "correctpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()

@patch("backend.src.database.DatabaseService.get_user_by_email", return_value=None)
def test_login_invalid_credentials(mock_get_user):
    response = client.post("/login", json={"email": "nonexistent@test.com", "password": "anypassword"})
    assert response.status_code == 401

# =========================
# Testes Usuário Autenticado
# =========================
def test_get_my_data_success():
    response = client.get("/users/me")
    assert response.status_code == 200
    assert "Olá user@example.com" in response.json()["message"]

@patch("backend.src.database.DatabaseService.get_user_skins", return_value=[
    {"id": 1, "name": "AK-47", "type": "Rifle", "float_value": "0.1", "owner_id": 5, "link": "img.png"},
    {"id": 2, "name": "M4A4", "type": "Rifle", "float_value": "0.2", "owner_id": 5, "link": "img.png"}
])
@patch("backend.src.database.DatabaseService.get_user_by_email", return_value=MockUser(5, "user@example.com"))
def test_get_inventory_success(mock_get_user, mock_get_skins):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.json()["skins"]) == 2

@patch("backend.src.database.DatabaseService.get_marketplace_skins", return_value=[{
    "id": 1, 
    "value": 100.0, 
    "name": "AWP",
    "type": "Sniper",
    "float_value": "Factory New",
    "owner_id": 99,
    "link": "http://image.com/awp.png"
}])
def test_get_marketplace_skins_success(mock_market):
    response = client.get("/marketplace/skins")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "AWP"

@patch("backend.src.database.DatabaseService.create_transaction")
@patch("backend.src.database.DatabaseService.get_user_by_email", return_value=MockUser(5, "user@example.com"))
def test_deposit_funds_success(mock_get_user, mock_create_transaction):
    # Agora com o override_get_db, o refresh(user) não vai crashar
    response = client.post("/wallet/deposit", json={"amount": 25.0})
    assert response.status_code == 200
    assert response.json()["new_balance"] == 125.0

# =========================
# Testes Compra
# =========================
@patch("backend.src.database.DatabaseService.buy_marketplace_skin", return_value=None)
@patch("backend.src.database.DatabaseService.get_user_by_email", return_value=MockUser(5, "user@example.com"))
def test_buy_skin_success(mock_get_user, mock_buy_skin):
    response = client.post("/marketplace/buy/skin/123")
    assert response.status_code == 200

@patch("backend.src.database.DatabaseService.buy_marketplace_skin", side_effect=ValueError("Insufficient funds"))
@patch("backend.src.database.DatabaseService.get_user_by_email", return_value=MockUser(5, "user@example.com"))
def test_buy_skin_not_enough_funds(mock_get_user, mock_buy_skin):
    response = client.post("/marketplace/buy/skin/123")
    assert response.status_code == 400

# =========================
# Testes Admin
# =========================
@patch("backend.src.database.DatabaseService.create_skin", return_value="50")
def test_admin_create_skin_success(mock_create_skin):
    response = client.post("/admin/skins", json={
        "name": "New Skin", 
        "float": "Factory New", 
        "type": "Knife",
        "link": "http://image.com/knife.png"
    })
    assert response.status_code == 201

@patch("backend.src.database.DatabaseService.edit_skin", return_value=None)
def test_admin_edit_skin_success(mock_edit_skin):
    # Como corrigimos o models.py, agora podemos enviar só campos parciais
    response = client.put("/admin/skin/edit/10", json={
        "float": "Minimal Wear",
        "name": "Updated Skin Name"
    })
    assert response.status_code == 200

@patch("backend.src.database.DatabaseService.delete_skin", side_effect=ValueError("Skin not found"))
def test_admin_delete_skin_not_found(mock_delete_skin):
    response = client.delete("/admin/skin/delete/999")
    assert response.status_code == 404