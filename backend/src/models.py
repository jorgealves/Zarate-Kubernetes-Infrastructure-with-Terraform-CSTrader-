from pydantic import BaseModel,Field,EmailStr,field_validator,ConfigDict
from typing import Optional,Dict

class User(BaseModel):
    id: int 
    name: str 
    email: EmailStr
    password: str
    role: str = "player"
    funds: float = 0.0
    @field_validator('name')
    @classmethod
    def validate_username(cls, v):
        """Validate username is not empty"""
        if not v or not v.strip():
            raise ValueError('Username cannot be empty')
        return v.strip()
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
                "role": "user",
                "funds": 100.0
            }

        }
    )
    
class skins(BaseModel):
    id: int
    name: str
    type: str
    float_value: float
    owner_id: int
    date_created: str
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "AK-47 | Redline",
                "type": "Rifle",
                "float": 0.15,
                "owner_id": 0
            }
        }
    )


class marketplace(BaseModel):
    id: int
    skin_id: int
    price: float
    listed_at: str

class RegisterRequest(BaseModel):
    name: str = Field(..., description="The name of the user")
    email: EmailStr = Field(..., description="The email of the user")
    password: str = Field(..., min_length=8, description="The password of the user")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePassword123#",
                "role":"player",
                "funds": 00.0
            }
        }
    )

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="The email of the user")
    password: str = Field(..., description="The password of the user")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john@example.com",
                "password": "SecurePassoword123#"
            }
        }
    )
    
class CreateSkinRequest(BaseModel):
    name: str = Field(..., description="The name of the skin example Dopler")
    type: str = Field(..., description="The type of the knife example (Bayonet, Karambit)")
    float_value: str = Field(..., alias="float", description="The float value of the skin Factory new, Minimal Wear, Field-Tested, Well-Worn, Battle-Scarred") 
    link: str = Field(..., description="The link to the skin image ")   
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True, 
        by_alias=True,
        json_schema_extra={
            "example": {
                "name": "Dopler",
                "type": "ButterFly",
                "float": "Factory new",
                "link":"https://example.com/skin_image.jpg"
            }
        }
    )
    
class EditSkinRequest(BaseModel):
    name: Optional[str] = Field(None, description="The name of the skin example Dopler")
    type: Optional[str] = Field(None, description="The type of the knife example (Bayonet, Karambit)")
    float_value: Optional[str] = Field(None, alias="float", description="The float value of the skin Factory new, Minimal Wear, Field-Tested, Well-Worn, Battle-Scarred")
    owner_id: Optional[int] = Field(None, description="The ID of the owner user") 
    link: Optional[str] = Field(None, description="The link to the skin image ")   
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True, 
        by_alias=True,
        json_schema_extra={
            "example": {
                "name": "Dopler",
                "type": "ButterFly",
                "float": "Factory new",
                "owner_id": 1,
                "link":"https://example.com/skin_image.jpg"
            }
        }
    )

class SkinDisplay(BaseModel):
    id: int
    name: str
    type: str
    float_value: Optional[str]
    owner_id: Optional[int]
    link: Optional[str]

    model_config = ConfigDict(
        from_attributes = True
    )
class DepositRequest(BaseModel):
    amount: float = Field(..., description="Amount to deposit")

    @field_validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        if v > 10000:
            raise ValueError("O valor máximo permitido é 10000.")
        return v


class MarketplaceSkinDisplay(BaseModel):
    id: int
    name: str
    type: str
    float_value: Optional[str]
    owner_id: Optional[int]
    link: Optional[str]
    value: float
    model_config = ConfigDict(
        from_attributes = True
    )

class AddMarketplaceSkinRequest(BaseModel):
    skin_id: int = Field(..., description="ID of the skin to be listed")
    value: float = Field(..., description="Listing price for the skin")

    @field_validator("value")
    def validate_value(cls, v):
        if v <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        return v
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "skin_id": 1,
                "value": 150.0
            }
        }
    )