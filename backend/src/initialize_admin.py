import sys
import os
from sqlalchemy.orm import Session
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")

from backend.src.database import DatabaseService, get_db
from backend.src.models import User, RegisterRequest 
from backend.src.utils.validation_utils import hash_password

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") 
ADMIN_NAME = os.getenv("ADMIN_NAME")

def create_initial_admin(db: Session):    
    db_service = DatabaseService()
    
    # 1. Verificar se o utilizador já existe
    existing_user = db_service.get_user_by_email(ADMIN_EMAIL, db) # Precisa de ajustar o get_user_by_email para aceitar a sessão
    
    if existing_user:
        print(f"INFO: Utilizador admin ({ADMIN_EMAIL}) já existe. Nada a fazer.")
        return

    print(f"INFO: A criar novo utilizador admin: {ADMIN_EMAIL}")
    
    password_hashed = hash_password(ADMIN_PASSWORD)
    
    admin_user = User(
        id=0,
        name=ADMIN_NAME,
        email=ADMIN_EMAIL,
        password=password_hashed,
        role="admin",
        funds=0.0
    )
    
    try:
        user_id = db_service.create_admin(admin_user, db) 
        print(f"SUCESSO: Utilizador admin criado com ID: {user_id}")
    except ValueError as e:
        print(f"ERRO: Falha ao criar admin. Detalhe: {e}")
    except Exception as e:
        print(f"ERRO: Erro inesperado ao criar admin: {e}")

if __name__ == "__main__":
    # Obtém uma sessão e executa a função.
    # Isto é feito fora do ciclo de vida do FastAPI para ser um script autónomo.
    try:
        # A função get_db é um generator, precisamos de o inicializar
        db_generator = get_db()
        db_session = next(db_generator) 
        
        create_initial_admin(db_session)
        
    except Exception as e:
        print(f"FALHA CRÍTICA: Não foi possível conectar ou criar o admin. A base de dados está a correr? Erro: {e}")