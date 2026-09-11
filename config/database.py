# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Altere as credenciais conforme seu servidor PostgreSQL
DB_USER = "postgres"
DB_PASS = "PnCdEL"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "hugelmanner_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()