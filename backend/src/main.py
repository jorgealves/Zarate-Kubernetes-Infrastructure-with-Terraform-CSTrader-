from typing import Union,Dict,List
from fastapi import FastAPI,Body, Request, status, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from fastapi.params import Depends
from backend.src.models import User, RegisterRequest, CreateSkinRequest,EditSkinRequest,SkinDisplay, DepositRequest,MarketplaceSkinDisplay,AddMarketplaceSkinRequest
from backend.src.utils.validation_utils import hash_password,verify_password
from backend.src.utils.security import get_current_user, get_current_admin_user
from backend.src.utils.auth_utils import create_access_token
from backend.src.database import DatabaseService, get_db
from fastapi.middleware.cors import CORSMiddleware

# Inicialização da Aplicação
app = FastAPI(
    title="CSTrader API MVP",
    description="API para Marketplace de Skins, com gestão de utilizadores, inventário e transações financeiras.",
    version="1.0.0"
)
db_service = DatabaseService()

# Configuração do CORS Middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            
    allow_credentials=True,           
    allow_methods=["*"],              
    allow_headers=["*"],              
)

# ----------------------------------------------------
# 1. ENDPOINTS DE AUTENTICAÇÃO E UTILIZADORES
# ----------------------------------------------------

@app.post("/register_user", status_code=status.HTTP_201_CREATED, response_model=Dict[str, str])
def register_user(
    user_data: RegisterRequest = Body(...,description="Dados de registo do utilizador (nome, email, password)"),
    db: Session = Depends(get_db) 
    ) -> Dict[str, str]:
    """
    Regista um novo utilizador na base de dados.

    - Faz o hash da password fornecida.
    - Cria um novo objeto User com role 'user' e fundos iniciais de 0.0.
    - Guarda o utilizador usando o DatabaseService.
    """
    # hash da password antes de guardar
    password_hashed = hash_password(user_data.password)
    new_user = User(
        id=0,
        name=user_data.name,
        email=user_data.email,
        password=password_hashed,
        role="user",
        funds=0.0
    )
    #Save user to database
    try:
        user_id = db_service.create_user(new_user,db)
        return {"message": "User registered successfully", "user_id": user_id}   
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Error creating user: {str(e)}") from e
    
@app.get("/get_user/{email}", status_code=status.HTTP_200_OK, response_model=Dict[str, Union[str, Dict]])
def get_user_by_email(email: str,current_user: dict = Depends(get_current_user) ,db: Session = Depends(get_db)) -> Dict[str, Union[str, Dict]]:
    """
    Recupera os detalhes de um utilizador específico pelo seu email.
    """
    try:
        user = db_service.get_user_by_email(email, db)
        if user:
            # Seleciona apenas dados seguros para retorno
            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "funds": user.funds
            }
            return {"message": "Utilizador recuperado com sucesso", "user": user_data}
        else:
            raise HTTPException(status_code=404, detail="Utilizador não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar utilizador: {str(e)}") from e


@app.post("/login",status_code=status.HTTP_200_OK)
def login_user(email: str = Body(..., embed=True), password: str = Body(..., embed=True), db: Session = Depends(get_db) ) -> Dict[str, str]:
    """
    Autentica um utilizador e emite um JWT (JSON Web Token).
    """
    try:
        user = db_service.get_user_by_email(email,db)
        # Verifica se o utilizador existe e se a password está correta
        if  user and verify_password(password,user.password):
            # Cria o token de acesso com o email e role no payload
            token = create_access_token({"sub": user.email, "role": user.role})
            return {"message": "Login bem-sucedido", "user_id": str(user.id), "access_token":token, "token_type":"bearer", "role": user.role}
        else:
            raise HTTPException(status_code=401, detail="Email ou password inválidos")
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.exception("ERRO NO LOGIN")
        raise

    

@app.get("/users/me")
def get_my_data(current_user: dict = Depends(get_current_user)):
    """
    Endpoint de teste para verificar se o token JWT é válido.
    Retorna os dados do utilizador autenticado.
    """
    return {"message": f"Olá {current_user['sub']}!"}


@app.get("/logout",status_code=status.HTTP_200_OK)
def logout_user(current_user: dict = Depends(get_current_user)) -> Dict[str, str]:
    """
    Simulação de Logout. Na prática, o token é descartado no lado do cliente.
    """
    return {"message": "Logout bem-sucedido"}


# ----------------------------------------------------
# 2. ENDPOINTS DE INVENTÁRIO E CARTEIRA
# ----------------------------------------------------

@app.get("/inventory", status_code=status.HTTP_200_OK, response_model=Dict[str, Union[str, List]])
def get_my_skins(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Union[str, List]]:
    """
    Recupera todas as skins que pertencem ao utilizador autenticado (o seu inventário).
    """
    try:
        user_email = current_user['sub']
        user = db_service.get_user_by_email(user_email, db)
        if not user:
            raise HTTPException(status_code=404, detail="Utilizador não encontrado")
        
        # Recupera as skins do inventário
        skins = db_service.get_user_skins(user.id, db)
        return {"message": "Skins do utilizador recuperadas com sucesso", "skins": skins}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar skins do utilizador: {str(e)}") from e
    
    
@app.get("/user/skins/{user_id}", status_code=status.HTTP_200_OK, response_model=Dict[str, Union[str, List]])
def get_user_skins_by_id(user_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Union[str, List]]:
    """
    Recupera as skins de qualquer utilizador pelo seu ID.
    """
    try:
        skins = db_service.get_user_skins(user_id, db)
        return {"message": "Skins do utilizador recuperadas com sucesso", "skins": skins}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar skins do utilizador: {str(e)}") from e
    
@app.post("/wallet/deposit", status_code=status.HTTP_200_OK)
def deposit_funds(
    deposit: DepositRequest = Body(..., description="Montante a depositar"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permite ao utilizador autenticado depositar fundos na sua carteira.

    - Atualiza o campo 'funds' do utilizador.
    - Regista a transação na tabela 'Transaction'.
    """
    try:
        user_email = current_user["sub"]
        user = db_service.get_user_by_email(user_email, db)

        if not user:
            raise HTTPException(status_code=404, detail="Utilizador não encontrado")

        # Atualizar saldo
        user.funds += deposit.amount
        db.commit()
        db.refresh(user)

        # Registrar transação na tabela Transaction
        db_service.create_transaction(
            user_id=user.id,
            amount=deposit.amount,
            transaction_type="deposit",
            db=db
        )

        return {
            "message": "Depósito realizado com sucesso.",
            "new_balance": user.funds
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar depósito: {str(e)}")
   
@app.get("/transactions/history", status_code=status.HTTP_200_OK, response_model=List[Dict[str, str]])
def get_transaction_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
    ) -> List[Dict[str, str]]:
    """
    Obtém o histórico de transações financeiras do utilizador autenticado.
    """
    try:
        user_email = current_user["sub"]
        user = db_service.get_user_by_email(user_email, db)

        if not user:
            raise HTTPException(status_code=404, detail="Utilizador não encontrado")

        transactions = db_service.get_transactions_by_user(user.id, db)

        return transactions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar histórico de transações: {str(e)}") from e


# ----------------------------------------------------
# 3. ENDPOINTS DE ADMINISTRAÇÃO (ADMIN ONLY)
# ----------------------------------------------------

@app.post("/admin/skins", status_code=status.HTTP_201_CREATED, response_model=Dict[str,Union[str, str]])
def create_skin_admin(
    skin_data: CreateSkinRequest = Body(..., description="Dados da skin base a ser criada"),
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
    ) -> Dict[str, Union[str, str]]:
    """
    [ADMIN ONLY] Cria uma nova skin base na base de dados (tabela 'Skin').
    """
    try:
        skin_id = db_service.create_skin(skin_data, db)
        return {"message": "Skin base criada com sucesso", "skin_id": skin_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar skin: {str(e)}")
    
@app.put("/admin/skin/edit/{skin_id}", status_code=status.HTTP_200_OK, response_model=Dict[str, str])
def edit_skin_admin(
    skin_id: int,
    skin_data: EditSkinRequest = Body(..., description="Dados da skin a serem atualizados"),
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
    ) -> Dict[str, str]:
    """
    [ADMIN ONLY] Edita os detalhes de uma skin base existente.
    """
    try:
        # Verifica se há campos para atualizar
        if not skin_data.model_dump(exclude_none=True, by_alias=True):
            raise HTTPException(status_code=400, detail="Nenhum campo fornecido para atualização.")
        
        db_service.edit_skin(skin_id, skin_data, db)
        return {"message": "Skin base atualizada com sucesso"}
    except ValueError as e:
        error_message = str(e)
        if "Skin not found" in error_message:
            raise HTTPException(status_code=404, detail=error_message)
        else:
            raise HTTPException(status_code=400, detail=error_message)
             
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar atualização: {str(e)}")
    
@app.get("/skins/all", status_code=status.HTTP_200_OK, response_model=List[SkinDisplay])
def get_all_skins(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user)
    ) -> Dict[str, List[str]]:
    """
    [ADMIN ONLY] Lista todas as skins base disponíveis no sistema.
    """
    try:
        skins = db_service.get_all_skins(db)
        return skins
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar skins base: {str(e)}") from e
    
@app.delete("/admin/skin/delete/{skin_id}", status_code=status.HTTP_200_OK, response_model=str)
def delete_skin_admin(
    skin_id: int,
    current_admin: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
    ) -> str:
    """
    [ADMIN ONLY] Elimina uma skin base pelo seu ID.
    """
    try:
        db_service.delete_skin(skin_id, db)
        return f"Skin base com id: {skin_id} eliminada com sucesso"
    except ValueError as e:
        error_message = str(e)
        if "Skin not found" in error_message:
            raise HTTPException(status_code=404, detail=error_message)
        else:
            raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao eliminar skin: {str(e)}") from e
    

# ----------------------------------------------------
# 4. ENDPOINTS DO MARKETPLACE
# ----------------------------------------------------

@app.get("/marketplace/skins", status_code=status.HTTP_200_OK, response_model=List[MarketplaceSkinDisplay])
def get_marketplace_skins(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
    ) -> Dict[str, List[str]]:
    """
    Lista todas as skins que estão ativamente disponíveis para compra no marketplace.
    """
    user_email = current_user['sub']
    try:
        skins = db_service.get_marketplace_skins(user_email,db)
        return skins
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar skins do marketplace: {str(e)}") from e


@app.post("/marketplace/add/skin", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Union[str, int]])
def marketplace_add_skin(
    skin_data: AddMarketplaceSkinRequest = Body(..., description="ID da UserSkin e valor de venda"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
    ) -> List[SkinDisplay]:
    """
    Adiciona uma skin do inventário do utilizador autenticado ao marketplace para venda.

    - A skin deve pertencer ao utilizador.
    - Cria um registo na tabela 'MarketplaceSkin'.
    """
    try:
        # A lógica de validação de posse e criação do registo está dentro do db_service
        skinId = db_service.add_marketplace_skin(skin_data.skin_id,skin_data.value, db)
        return {"message": "Skin adicionada com sucesso ao mercado", "skin_id": int(skinId)}
    except ValueError as e:
        # Erros como "Skin não encontrada" ou "Skin não pertence ao utilizador"
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar skin ao mercado: {str(e)}") from e
    
    
@app.delete("/marketplace/remove/skin/{marketplace_skin_id}", status_code=status.HTTP_200_OK, response_model=Dict[str, str])
def marketplace_remove_skin(
    marketplace_skin_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
    ) -> Dict[str, str]:
    """
    Remove uma skin que o utilizador autenticado listou para venda do marketplace.

    - A skin deve estar listada e pertencer ao utilizador (verificação feita em db_service).
    - Elimina o registo na tabela 'MarketplaceSkin'.
    """
    try:
        db_service.remove_marketplace_skin(marketplace_skin_id, db)
        return {"message": "Skin removida com sucesso do mercado"}
    
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg or "not listed" in error_msg:
             raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
        
    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover skin: {str(e)}") from e

@app.post("/marketplace/buy/skin/{marketplace_skin_id}", status_code=status.HTTP_200_OK, response_model=Dict[str, str])
def marketplace_buy_skin(
    marketplace_skin_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
    ) -> Dict[str, str]:
    """
    Processa a compra de uma skin listada no marketplace.

    - **Fluxo Atómico e Crítico:** Verifica fundos, transfere a skin (atualiza o owner_id da UserSkin),
      e registra as transações de débito/crédito.
    """
    try:
        user_email = current_user["sub"]
        user = db_service.get_user_by_email(user_email, db)

        if not user:
            raise HTTPException(status_code=404, detail="Utilizador não encontrado")

        # Lógica de compra, transferência e transação
        db_service.buy_marketplace_skin(marketplace_skin_id, user.id, db)

        return {"message": "Skin comprada com sucesso"}
    except HTTPException:
        raise
    except ValueError as e:
        error_message = str(e)
        if "not found" in error_message:
            raise HTTPException(status_code=404, detail=error_message)
        # Erro de fundos insuficientes ou outra validação
        else:
            raise HTTPException(status_code=400, detail=error_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao comprar skin: {str(e)}") from e
    
@app.get("/marketplace/user/skins", status_code=status.HTTP_200_OK, response_model=List[MarketplaceSkinDisplay])
def get_my_marketplace_skins(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
    ) -> Dict[str, List[str]]:
    """
    Lista todas as skins que o utilizador autenticado colocou à venda.
    """
    user_email = current_user['sub']
    try:
        skins = db_service.get_user_marketplace_skins(user_email,db)
        return skins
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar skins listadas: {str(e)}") from e
