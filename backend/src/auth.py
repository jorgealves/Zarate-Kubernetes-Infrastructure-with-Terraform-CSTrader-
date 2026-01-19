from typing import Union,Dict
from fastapi import FastAPI,Body, Request, status, HTTPException
from models import User, RegisterRequest
from src.utils.validation_utils import hash_pasword,validate_email_format,validate_password_strength
from backend.src.database import Database
from contextlib import asynccontextmanager

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database()
    yield
    app.state.db.close()
app = FastAPI(lifespan=lifespan)

@app.post("/register_user", status_code=status.HTTP_201_CREATED, response_model=Dict[str, str])
def register_user(
    user_data: RegisterRequest = Body(...,description="User registration data"),
    request: Request = None
    ) -> Dict[str, str]:
    #Validate email format
    if not validate_email_format(user_data.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    #Validate password strength
    if not validate_password_strength(user_data.password):
        raise HTTPException(status_code=400, detail="Password does not meet strength requirements")
    
    #Validate if user with email already exists
    """
    try:
        db_instance = request.app.state.db
        existing_user = db_instance.check_user_exists(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error checking existing user") from e
    """
    
    #hash password
    password_hashed = hash_pasword(user_data.password)
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
        db_instance = request.app.state.db
        user_id = db_instance.create_user(new_user)
        return {"message": "User registered successfully", "user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {e}")
