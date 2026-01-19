from sqlalchemy import Column, Integer, String, Float, DateTime,ForeignKey
import sqlalchemy.orm 
from datetime import datetime,timezone

Base = sqlalchemy.orm.declarative_base()

class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="player")
    funds = Column(Float, default=0.0)
    date_created = Column(DateTime, default=datetime.now(timezone.utc)) 


class SkinTable(Base):
    __tablename__ = "skins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    float_value = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date_created = Column(DateTime, default=datetime.now(timezone.utc))
    link = Column(String,default="https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XuWbwcuyMESA4Fdl-4nnpU7iQA3-kKnr8ytd6s2te7cjd6HHXmHBxep157VtTi_rzUR-5WiHnt39c3_EZg4pW5UjQOZbsBCxw8qnab32FBG7RA/280x210")
    marketplace_items = sqlalchemy.orm.relationship(
        "Marketplace", backref="skin", cascade="all, delete"
    )
     
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.now(timezone.utc))

class Marketplace(Base):
    __tablename__ = "marketplace"

    id = Column(Integer, primary_key=True,index=True)
    skin_id = Column(Integer,ForeignKey('skins.id', ondelete="CASCADE"), nullable=False)
    value = Column(Float, nullable = False)