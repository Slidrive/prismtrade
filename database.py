from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base
import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///trading.db')

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DBSession:
    def __enter__(self):
        self.db = SessionLocal()
        return self.db
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        self.db.close()
