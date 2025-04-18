from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas, auth
import db
models.Base.metadata.create_all(bind=db.engine)
app = FastAPI()

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@app.post("/auth/register", response_model=schemas.Token)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed_pw)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    token = auth.create_access_token({"sub": new_user.email})
    return {"access_token": token}


@app.post("/auth/login", response_model=schemas.Token)
async def login(form: schemas.UserLogin, db: Session = Depends(get_db)):
    user = await db.execute(
        db.query(models.User).filter(models.User.email == form.username)
    )
    user = user.scalar_one_or_none()
    if not user or not auth.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token}
