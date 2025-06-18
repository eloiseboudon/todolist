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

@router.get("/active", response_model=Category)
def get_categorie(category_id:int, db: Session = Depends(get_db)):
    categories = db.query(models.Category).filter(models.Category.is_active == True).all()
    return categories


@router.get("/{category_id}", response_model=Category)
def get_categorie(category_id:int, db: Session = Depends(get_db)):
    categorie = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not categorie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Category not found"
        )
    return categorie

