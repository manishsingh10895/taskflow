from shared.db import Base, engine
import db
# from shared.models import User, UserProfile
import shared.models

# SessionLocal = db.SessionLocal()
# SessionLocal.query(User).delete()
# SessionLocal.query(UserProfile).delete()
# SessionLocal.commit()

print(Base.metadata.tables.keys())

Base.metadata.drop_all(bind=engine)

Base.metadata.clear()
# Base.metadata.create_all(bind=engine)

print("Database reset complete.")
