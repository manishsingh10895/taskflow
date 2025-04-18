from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[3] / ".env"

print("Loading environment variables from:", env_path)
if not env_path.exists():
    print(
        "Warning: .env file not found. Make sure to create one with the necessary variables."
    )

load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

print(DATABASE_URL)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
