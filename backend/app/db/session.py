import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Ajout de gestion d'erreur
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Configuration plus robuste pour la production
engine = create_engine(
    DATABASE_URL, 
    echo=True,  # Mettre à False en production
    pool_pre_ping=True,  # Vérifie les connexions
    pool_recycle=300     # Recycle les connexions après 5min
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction utilitaire pour créer toutes les tables
def create_tables():
    Base.metadata.create_all(bind=engine)