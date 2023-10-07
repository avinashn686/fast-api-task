from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from tempfile import NamedTemporaryFile
import shutil
from bson import ObjectId
from pydantic import BaseModel
import io
from urllib.parse import quote
from base64 import b64encode

DATABASE_URL = "postgresql://postgres:password@localhost/mydatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String)

Base.metadata.create_all(bind=engine)

client = MongoClient("mongodb://localhost:27017/")
mongo_db = client["user_profiles"]
profile_collection = mongo_db["profiles"]

app = FastAPI()

class UserCreate(BaseModel):
    first_name: str
    email: str
    password: str
    phone: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    email: str
    phone: str
    profile_picture_url: str 

@app.post("/register")
async def register_user(
    first_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: str = Form(...),
    profile_picture: UploadFile = File(...),
):
    user_data = {
        "first_name": first_name,
        "email": email,
        "password": password,
        "phone": phone,
    }

    existing_user = SessionLocal().query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(**user_data)
    db = SessionLocal()
    db.add(db_user)
    db.commit()
    db.refresh(db_user)


    with NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(profile_picture.file, temp_file)
        temp_file.seek(0)
        
        file_binary_data = temp_file.read()


        file_id = profile_collection.insert_one({
            "user_id": db_user.id,
            "profile_picture": file_binary_data,
            "content_type": profile_picture.content_type,
        }).inserted_id

    return {"user_id": str(db_user.id), "profile_picture_id": str(file_id)}



@app.get("/users")
async def list_users():

    db_users = SessionLocal().query(User).all()
    
    user_responses = []
    
    for user in db_users:

        profile = profile_collection.find_one({"user_id": user.id})
        profile_picture_data = profile.get("profile_picture") if profile else None
        

        if profile_picture_data:
            content_type = profile.get("content_type")
            base64_image = b64encode(profile_picture_data).decode("utf-8")
            profile_picture_url = f"data:{content_type};base64,{quote(base64_image)}"
        else:
            profile_picture_url = None
        
        user_response = UserResponse(
            id=user.id,
            first_name=user.first_name,
            email=user.email,
            phone=user.phone,
            profile_picture_url=profile_picture_url,
        )
        
        user_responses.append(user_response)
    
    return user_responses