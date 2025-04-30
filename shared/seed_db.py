# Insert random details in the database,
# Task, User, and Project
# using the faker library

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from faker import Faker
import random
import hashlib
import os
from dotenv import load_dotenv
from shared.db import Base, engine
from shared.models import User, UserProfile, Task, Project
from passlib.context import CryptContext

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not set in .env file")

# Create a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create a new Faker instance
fake = Faker()


def email_hash(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()


# Create a new session
def create_session():
    session = SessionLocal()
    return session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def main():
    # Create a new session
    session = create_session()

    # Create random users
    for _ in range(10):
        email = fake.email()
        gravatar_url = (
            f"https://www.gravatar.com/avatar/{email_hash(email=email)}?d=identicon"
        )
        user = User(
            username=fake.user_name(),
            email=email,
            password=hash_password("terminator"),
        )
        session.add(user)
        session.commit()

        # Create random user profiles
        user_profile = UserProfile(
            user_id=user.id,
            bio=fake.text(),
            avatar_url=gravatar_url,
            full_name=fake.name(),
        )
        session.add(user_profile)
        session.commit()

    # Create random projects
    for _ in range(5):
        project = Project(
            name=fake.company(),
            description=fake.text(),
            user_id=random.randint(1, 10),  # Assuming you have 10 users
        )
        session.add(project)
        session.commit()

        # Create random tasks
        for _ in range(3):
            task = Task(
                title=fake.sentence(),
                description=fake.text(),
                completed=False,
                user_id=random.randint(1, 10),  # Assuming you have 10 users
                project_id=project.id,
            )
            session.add(task)
            session.commit()

    # Close the session
    session.close()


if __name__ == "__main__":
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Call the main function to seed the database
    try:
        main()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the session
        print("Closing session.")