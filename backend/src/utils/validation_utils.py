from passlib.context import CryptContext
import re
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    if isinstance(password, tuple) and len(password) > 0:
        password = password[0]
        
    if not isinstance(password, str):
        password = str(password)
    
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> bool:
    pattern = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$'
    )
    return bool(pattern.match(password))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



def validate_email_format(email: str) -> bool:
    # Simple email format validation
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None
