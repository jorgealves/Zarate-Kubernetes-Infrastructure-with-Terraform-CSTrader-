# Importações necessárias para o framework de testes e mocking
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Dict

# Presume-se que o serviço e os modelos são importáveis a partir da sua estrutura
# NOTA: Ajuste as importações para o caminho correto do seu projeto (backend/src/...)
from backend.src.database import DatabaseService 

# --- SIMULAÇÕES NECESSÁRIAS PARA O TESTE ---
# Geralmente, estas classes viriam de 'backend.src.models' e 'backend.src.db_models'
# Ajustei a importação para refletir uma estrutura comum de monorepo.

class MockUser:
    """Simulação do modelo Pydantic 'User'."""
    def __init__(self, name="Test User", email="test@example.com", password="hashed_password", role="user", funds=100.0):
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.funds = funds

class MockUserTable:
    """Simulação do modelo ORM 'UserTable'."""
    id: int = None 
    name: str = "Test User"
    email: str = "test@example.com"
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            
# --- FIXTURES (Dependências) ---

@pytest.fixture
def db_service():
    """Fixture que fornece uma instância do DatabaseService."""
    # Presume-se que DatabaseService() inicializa corretamente com as suas dependências (settings, etc.)
    return DatabaseService()

@pytest.fixture
def mock_session() -> MagicMock:
    """Fixture que fornece uma sessão SQLAlchemy simulada (mock)."""
    return MagicMock(spec=Session)

@pytest.fixture
def mock_user_data() -> MockUser:
    """Fixture que fornece dados Pydantic simulados de um utilizador."""
    return MockUser()



def test_create_user_success(db_service: DatabaseService, mock_session: MagicMock, mock_user_data: MockUser):
    """
    Testa a criação bem-sucedida de um novo utilizador.

    Simulamos o db.refresh() para injetar o ID no objeto ORM criado.
    """
    EXPECTED_ID = 101
    
    def mock_refresh_side_effect(obj_to_refresh):
        obj_to_refresh.id = EXPECTED_ID

    mock_session.refresh.side_effect = mock_refresh_side_effect
    user_id = db_service.create_user(mock_user_data, mock_session)
    assert user_id == str(EXPECTED_ID) 
    
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_create_user_integrity_error(db_service: DatabaseService, mock_session: MagicMock, mock_user_data: MockUser):
    """
    Testa o tratamento de erro quando o email já existe (IntegrityError).
    """
    mock_session.commit.side_effect = IntegrityError("message", "params", "orig")

    with pytest.raises(ValueError, match="User with this email already exists"):
        db_service.create_user(mock_user_data, mock_session)

    mock_session.rollback.assert_called_once()


def test_get_user_by_email_found(db_service: DatabaseService, mock_session: MagicMock):
    """
    Testa a recuperação bem-sucedida de um utilizador por email.
    """
    expected_user = MockUserTable(id=202, email="found@example.com")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_user 
    mock_session.execute.return_value = mock_result
    
    result = db_service.get_user_by_email("found@example.com", mock_session)
    assert result is expected_user
    assert result.id == 202
    mock_session.execute.assert_called_once()


def test_get_user_by_email_not_found(db_service: DatabaseService, mock_session: MagicMock):
    """
    Testa a recuperação de um utilizador que não existe.
    """
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    result = db_service.get_user_by_email("not_found@example.com", mock_session)
    assert result is None
    mock_session.execute.assert_called_once()
