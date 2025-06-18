from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import Category, CategoryCreate, CategoryUpdate
from app.db import models
from app.db.session import get_db
from typing import List

router = APIRouter()

@router.get("/", response_model=List[Category])
def get_categories(db: Session = Depends(get_db)):
    """Récupérer toutes les catégories"""
    categories = db.query(models.Category).all()
    return categories
