from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import CategoryCreate
from sqlalchemy import func
from app.db import models
from app.db.session import get_db
from typing import List
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.get("/", response_model=List[CategoryCreate]) 
def get_categories(db: Session = Depends(get_db)):
    """Récupérer toutes les catgories"""
    return db.query(models.Category).order_by(models.Category.id).all()
