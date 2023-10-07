from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel

DATABASE_URL = "postgresql://postgres:password@localhost/mydatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users1"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String)

    profiles1 = relationship("Profile", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles1"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users1.id"))
    profile_picture = Column(String)

    user = relationship("User", back_populates="profiles1")

Base.metadata.create_all(bind=engine)

app = FastAPI()

class UserCreate(BaseModel):
    first_name: str
    email: str
    password: str
    phone: str



class RegistrationResponse(BaseModel):
    message: str  

@app.post("/register", response_model=RegistrationResponse)  
async def register_user(
    first_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: str = Form(...),
    profile_picture: UploadFile = File(...)
):
    user_data = UserCreate(
        first_name=first_name,
        email=email,
        password=password,
        phone=phone
    )
    
    db_user = User(**user_data.dict())
    
  
    existing_user = SessionLocal().query(User).filter(
        (User.email == email) | (User.phone == phone)
    ).first()
    
    if existing_user:
        return RegistrationResponse(message="Registration failed. Email or Phone already registered")
    

    db = SessionLocal()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
   
    if profile_picture:
        profile_picture_content = profile_picture.file.read()
        profile = Profile(user_id=db_user.id, profile_picture=profile_picture_content)
        db.add(profile)
        db.commit()
    
    return RegistrationResponse(message="Registration successful")

@app.get("/user/{user_id}")
async def get_user(user_id: int):

    db_user = SessionLocal().query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    profiles = db_user.profiles1 
    profile_picture = profiles[0].profile_picture if profiles else None
    
    return {
        "user": db_user,
        "profile_picture": profile_picture
    }

@app.get("/users")
async def get_users():

    db_users = SessionLocal().query(User).all()
    return db_users