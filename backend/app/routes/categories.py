from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import Category, CategoryCreate, CategoryUpdate
from app.db import models
from app.db.session import get_db
from typing import List

router = APIRouter()


@router.post("/", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle catégorie"""
    db_category = models.Category(**category.model_dump())
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error creating category")

@router.get("/", response_model=List[Category])
def get_categories(db: Session = Depends(get_db)):
    """Récupérer toutes les catégories"""
    categories = db.query(models.Category).all()
    return categories

@router.get("/active", response_model=List[Category])
def get_categorie_active(db: Session = Depends(get_db)):
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

