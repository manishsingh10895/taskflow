from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import shared.db as db
import shared.auth_utils as auth_utils
from shared.logger import logger
import shared.models as models
import schemas
import auth

db.Base.metadata.create_all(bind=db.engine)

app = FastAPI()

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@app.post("/auth/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info("Registering new user")
    logger.info(user)
    existing = (
        db.query(models.User)
        .filter(
            (models.User.email == user.email) | (models.User.username == user.username)
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(email=user.email, username=user.username, password=hashed_pw)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = auth.create_access_token({"sub": str(new_user.id)})
    return {"access_token": token}


@app.get("/auth/me", response_model=schemas.User)
def get_current_user(token: str, db: Session = Depends(get_db)):
    logger.info("Getting current user")
    logger.info(token)
    email = auth_utils.get_token_payload(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.email == email).first()

    logger.info(user)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
    }


@app.post("/auth/login", response_model=schemas.Token)
def login(form: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.execute(db.query(models.User).filter(models.User.email == form.username))
    user = user.scalar_one_or_none()
    if not user or not auth.verify_password(form.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token}
