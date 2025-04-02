from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware



# Database setup
DATABASE_URL = "sqlite:///./test.db"  # SQLite database file

# Create the SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the SQLAlchemy model for the "users" table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    amount = Column(Float, index=True)
    
# Create the tables in the database
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3000",  # URL of your React app (Frontend)
    "http://frontend-service:80",
    "http://localhost",
    "http://127.0.0.1"
]

# Add CORS middleware to allow cross-origin requests from the React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now, you can restrict it later
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Pydantic model to validate request data (input)
class UserCreate(BaseModel):
    name: str
    email: str
    amount: float

    class Config:
        orm_mode = True  # Tells Pydantic to treat SQLAlchemy models as dicts

# Pydantic model to return data in the response
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    amount: float
    
    class Config:
        orm_mode = True  # Tells Pydantic to treat SQLAlchemy models as dicts

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST API to create a new user and store it in the database
#inject dependencies (e.g.,database connections) into your API endpoint functions
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create a new user object
    new_user = User(name=user.name, email=user.email, amount=user.amount)
    
    # Add the new user to the session and commit
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # To get the data with the generated ID
    
    return new_user  # Return the created user as a response

# GET API to retrieve all users from the database
@app.get("/users/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()  # Fetch all users from the "users" table
    return users
