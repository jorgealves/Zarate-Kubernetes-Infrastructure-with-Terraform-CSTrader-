from backend.src.settings import settings
from backend.src.models import User, CreateSkinRequest,EditSkinRequest
from backend.src.db_models import UserTable, SkinTable, Transaction, Marketplace
from sqlalchemy import create_engine, select, insert,text,distinct
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import List, Dict
from datetime import datetime,timezone
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = (
        f"{settings.database_driver}://"
        f"{settings.database_username}:{settings.database_password}@"
        f"{settings.database_host}:{settings.database_port}/"
        f"{settings.database_name}"
    )

# Criação do Engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Criação da Sessão Local para a DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class DatabaseService:
    """
    Classe de Serviço de Base de Dados (DatabaseService)

    Esta classe encapsula todas as interações CRUD (Create, Read, Update, Delete)
    e lógica de negócio complexa que envolve a persistência de dados.
    """
    def __init__(self):
        """Inicialização do serviço."""
        pass
        
    def create_user(self, user: User, db: Session) -> str:       
        """Cria um novo utilizador na tabela UserTable."""
        try:
            db_user = UserTable(
                name=user.name,
                email=user.email,
                password=user.password,
                role=user.role,
                funds=user.funds
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return str(db_user.id)
        except IntegrityError as e:
                # Rollback em caso de erro de integridade (e.g., email duplicado)
                db.rollback()
                raise ValueError("User with this email already exists") from e
    
    def create_admin(self, user: User, db: Session) -> str:       
        """Cria um utilizador com a role de administrador. (Uso restrito)."""
        try:
            db_user = UserTable(
                id=user.id,
                name=user.name,
                email=user.email,
                password=user.password,
                role=user.role,
                funds=user.funds
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return str(db_user.id)
        except IntegrityError as e:
                db.rollback()
                raise ValueError("Administrador com este id ou email já existe") from e
    
    def get_user_by_email(self, email: str, db: Session) -> UserTable | None:
        """Busca um utilizador na DB pelo seu endereço de email."""
        try:
            query = select(UserTable).where(UserTable.email == email)
            result = db.execute(query).scalar_one_or_none()  
            return result
        except Exception as e:
            raise ValueError(f"Erro ao buscar utilizador por email: {str(e)}")

        
    def get_all_users(self,db: Session) -> List[Dict]:
        """Recupera e formata todos os registos de utilizadores."""
        query = select(UserTable)
        db_users = db.scalars(query).all()
        users_data = []
        for user in db_users:
            # Filtra os dados sensíveis (e.g., password) antes de retornar
            users_data.append({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "funds": user.funds
            })
        return users_data
    
    def get_user_skins(self,user_id:int,db: Session) -> List[Dict]:
        """
        Recupera as skins de um utilizador, excluindo aquelas que estão listadas
        ativamente no marketplace (tabela Marketplace).
        """
        query_skins = (
            select(SkinTable)
            .outerjoin(Marketplace, Marketplace.skin_id == SkinTable.id)
            .where(
                SkinTable.owner_id == user_id, 
                Marketplace.skin_id == None # Apenas onde não há correspondência no Marketplace (não listado)
            )
        )
        db_skins = db.scalars(query_skins).all()
        skins_data = []
        for skin in db_skins:
            skins_data.append({
                "id": skin.id,
                "name": skin.name,
                "type": skin.type,
                "float_value": skin.float_value,
                "owner_id": skin.owner_id,
                "date_created": skin.date_created,
                "link": skin.link
            })
        return skins_data
    
    def create_skin(self, skin: CreateSkinRequest, db: Session) -> str:       
        """Cria uma nova skin base na tabela SkinTable (usada por admins)."""
        try:
            db_skin = SkinTable(
                name=skin.name,
                type=skin.type,
                float_value=skin.float_value,
                owner_id=0, # ID 0 pode ser um owner "admin/system"
                date_created=datetime.now(timezone.utc),
                link=skin.link
            )
            db.add(db_skin)
            db.commit()
            db.refresh(db_skin)
            return str(db_skin.id)
        except IntegrityError as e:
                db.rollback()
                raise ValueError("Erro ao criar skin") from e
            
    def edit_skin(self, skin_id: int, skin: EditSkinRequest, db: Session) -> str:
        """Atualiza os detalhes de uma skin base pelo ID."""
        try:
            skin_update = db.get(SkinTable, skin_id)
            if not skin_update:
                raise ValueError("Skin não encontrada")
            
            # Atualiza apenas os campos que não são None
            if skin.name is not None:
                skin_update.name = skin.name
            if skin.type is not None:
                skin_update.type = skin.type
            if skin.float_value is not None:
                skin_update.float_value = skin.float_value 
            if skin.owner_id is not None:
                skin_update.owner_id = skin.owner_id
            if skin.link is not None:
                skin_update.link = skin.link  
                
            db.commit()
            return str(skin_id) 
            
        except IntegrityError as e:
            db.rollback()
            raise ValueError("Erro ao atualizar skin (possível owner_id inválido)") from e
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao atualizar skin: {str(e)}") from e
        
    def get_all_skins(self,db: Session) -> List[Dict]:
        """Recupera todas as skins base, ordenadas por tipo."""
        query = select(SkinTable).order_by(SkinTable.type)
        result = db.execute(query).scalars().all()
        return result
    
    def delete_skin(self, skin_id: int, db: Session) -> None:
        """Elimina uma skin base pelo ID."""
        try:
            skin_to_delete = db.get(SkinTable, skin_id)
            if not skin_to_delete:
                raise ValueError("Skin não encontrada")
            db.delete(skin_to_delete)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao eliminar skin: {str(e)}") from e
        
    def create_transaction(self, user_id: int, amount: float, transaction_type: str, db: Session):
        """Cria um novo registo de transação (depósito, compra ou venda)."""
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type=transaction_type,
            date=datetime.now(timezone.utc) # Adicionado timestamp
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction.id
    
    def get_marketplace_skins(self, user_email: str, db: Session) -> List[Dict]:
        """
        Recupera todas as skins listadas no marketplace, excluindo aquelas
        que pertencem ao utilizador que está a consultar.
        """
        try:
            # 1. Obter o ID do utilizador logado
            query = select(UserTable.id).where(UserTable.email == user_email)
            user_id = db.execute(query).scalar_one_or_none()
            
            # 2. Consultar skins no marketplace onde o owner_id não é o ID do utilizador
            query = (
                select(SkinTable.id, SkinTable.name, SkinTable.type, SkinTable.float_value, 
                       SkinTable.date_created, SkinTable.link, SkinTable.owner_id, Marketplace.value, Marketplace.id.label('marketplace_skin_id'))
                .join(Marketplace, Marketplace.skin_id == SkinTable.id)
                .where(SkinTable.owner_id != user_id)
            )
            result = db.execute(query)
            
            skins_data = []
            for row in result:
                skins_data.append({
                    "id": row.id,
                    "name": row.name,
                    "type": row.type,
                    "float_value": row.float_value,
                    "date_created": row.date_created,
                    "owner_id": row.owner_id,
                    "link": row.link,
                    "value": row.value,
                    "marketplace_skin_id": row.marketplace_skin_id # Importante para compra/remoção
                })
            return skins_data
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao buscar skins do marketplace: {str(e)}") from e
        
    def add_marketplace_skin(self, skin_id: int, value: float, db : Session ) -> str :
        """
        Adiciona uma skin à listagem do marketplace.

        Verifica se a skin já está listada antes de adicionar para evitar duplicados.
        """
        try:
            # 1. Verifica se a skin já está no marketplace
            verify_existing_skin_query = select(Marketplace.id).where(Marketplace.skin_id == skin_id)
            verify_existing_skin = db.execute(verify_existing_skin_query).scalar_one_or_none()
            if verify_existing_skin:
                raise ValueError(f"Skin com id: {skin_id} já está listada no marketplace")
                
            # 2. Cria o novo registo de marketplace
            marketplace_skin = Marketplace(
                skin_id=skin_id,
                value=value
            )
            db.add(marketplace_skin)
            db.commit()
            db.refresh(marketplace_skin)
            return str(marketplace_skin.id)
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao adicionar skin ao marketplace: {str(e)}") from e
        
    def buy_marketplace_skin(self, skin_id: int, buyer_id: int, db: Session) -> None:
        """
        [OPERAÇÃO CRÍTICA/ATÓMICA] Processa a compra de uma skin no marketplace.

        Este método garante que a transferência de fundos, a mudança de propriedade
        e a remoção da listagem ocorram todas com sucesso (atomicidade da transação).
        """
        try:
            # 1. Recupera a listagem do marketplace
            marketplace_skin_query = select(Marketplace).where(Marketplace.skin_id == skin_id)
            marketplace_skin = db.execute(marketplace_skin_query).scalar_one_or_none()
            if not marketplace_skin:
                raise ValueError(f"Skin com id: {skin_id} não está listada no marketplace")
                
            # 2. Recupera a Skin, Comprador e Vendedor
            skin = db.get(SkinTable, skin_id)
            buyer = db.get(UserTable, buyer_id)
            
            if not skin:
                raise ValueError(f"Skin com id: {skin_id} não existe")
            if not buyer:
                raise ValueError(f"Comprador com id: {buyer_id} não existe")
                
            value = marketplace_skin.value
            
            if buyer.funds < value:
                raise ValueError("O comprador não tem fundos suficientes")
                
            seller = db.get(UserTable, skin.owner_id)
            if not seller:
                # Isto não deve acontecer se a FK estiver configurada corretamente
                raise ValueError(f"Vendedor com id: {skin.owner_id} não existe") 
                
            # 3. Executa as operações financeiras e de propriedade
            
            # Débito no comprador
            buyer.funds -= value
            # Crédito no vendedor
            seller.funds += value
            # Transferência de propriedade da skin
            skin.owner_id = buyer_id
            
            # 4. Regista as transações
            transaction_query_buyer = Transaction(
                user_id=buyer_id,
                amount= -value, # Débito é valor negativo
                type="purchase"
            )
            transaction_query_seller = Transaction(
                user_id=seller.id,
                amount= value, # Crédito é valor positivo
                type="sale"
            )
            db.add(transaction_query_buyer)
            db.add(transaction_query_seller)
            
            # 5. Remove a skin da listagem do marketplace
            db.delete(marketplace_skin)
            
            # 6. Finaliza a transação atómica
            db.commit()
        except Exception as e:
            # Rollback em qualquer falha para reverter todas as alterações
            db.rollback()
            raise ValueError(f"Erro ao comprar skin do marketplace: {str(e)}") from e
        
    def remove_marketplace_skin(self, marketplace_skin_id: int, db: Session) -> None:
        """Remove uma skin da listagem do marketplace (cancelamento de venda)."""
        try:
            # Assume que o marketplace_skin_id é o ID do registo na tabela Marketplace
            marketplace_skin = db.get(Marketplace, marketplace_skin_id) 

            if not marketplace_skin:
                raise ValueError(f"Registo de marketplace com id: {marketplace_skin_id} não encontrado")
            
            db.delete(marketplace_skin)
            db.commit()
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao remover skin do marketplace: {str(e)}") from e
        
    def get_user_marketplace_skins(self, user_email: str, db: Session) -> List[Dict]:
        """Recupera as skins listadas para venda pelo utilizador autenticado."""
        try:
            query_user = select(UserTable.id).where(UserTable.email == user_email)
            user_id = db.execute(query_user).scalar_one_or_none()
            if user_id is None:
                raise ValueError(f"Utilizador com email: {user_email} não existe")
            
            # Consulta por skins onde o owner_id é o utilizador, E estão no Marketplace
            query = (
                select(SkinTable.id, SkinTable.name, SkinTable.type, SkinTable.float_value, 
                       SkinTable.date_created, SkinTable.link, SkinTable.owner_id, Marketplace.value, Marketplace.id.label('marketplace_skin_id'))
                .join(Marketplace, Marketplace.skin_id == SkinTable.id)
                .where(SkinTable.owner_id == user_id)
            )
            result = db.execute(query)
            
            skins_data = []
            for row in result:
                skins_data.append({
                    "id": row.id,
                    "name": row.name,
                    "type": row.type,
                    "float_value": row.float_value,
                    "date_created": row.date_created,
                    "owner_id": row.owner_id,
                    "link": row.link,
                    "value": row.value,
                    "marketplace_skin_id": row.marketplace_skin_id
                })
            return skins_data
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao buscar skins listadas pelo utilizador: {str(e)}") from e
        
    def get_transactions_by_user(self, user_id: int, db: Session) -> List[Dict]:
        """Recupera o histórico de transações de um utilizador, ordenado por data."""
        try:
            query = select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.date.desc())
            result = db.execute(query).scalars().all()
            transactions_data = []
            for transaction in result:
                transactions_data.append({
                    "id": str(transaction.id),
                    "user_id": str(transaction.user_id),
                    "amount": str(transaction.amount),
                    "type": str(transaction.type),
                    "date": str(transaction.date)
                })
            return transactions_data
        except Exception as e:
            db.rollback()
            raise ValueError(f"Erro ao buscar transações para o utilizador {user_id}: {str(e)}") from e

# Alias para facilitar o uso
Database = DatabaseService

def get_db():
     """
     Função 'yield' de dependência do FastAPI para gerir a sessão de DB.
     Garante que a sessão é fechada após a requisição.
     """
     db = SessionLocal()
     try:
         yield db
     finally:
         db.close()
         
if __name__ == "__main__":
    # Ponto de paragem para debug
    breakpoint()
