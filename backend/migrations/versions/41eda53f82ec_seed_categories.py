"""seed categories

Revision ID: 41eda53f82ec
Revises: f2548e99db0e
Create Date: 2025-06-18 13:09:59.151902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.db.models import Category 
# Données des catégories
CATEGORIES_DATA = [
    {
        "name": "Travail",
        "color": "#1E40AF",
        "icon": "briefcase",
        "description": "Tâches professionnelles et projets de travail",
        "is_active": True
    },
    {
        "name": "Réunions",
        "color": "#7C3AED",
        "icon": "users",
        "description": "Rendez-vous, réunions et entretiens",
        "is_active": True
    },
    {
        "name": "Formation",
        "color": "#059669",
        "icon": "book-open",
        "description": "Apprentissage et développement professionnel",
        "is_active": True
    },
    {
        "name": "Personnel",
        "color": "#DC2626",
        "icon": "heart",
        "description": "Tâches personnelles et bien-être",
        "is_active": True
    },
    {
        "name": "Famille",
        "color": "#F59E0B",
        "icon": "home",
        "description": "Activités et obligations familiales",
        "is_active": False
    },
    {
        "name": "Amis",
        "color": "#EC4899",
        "icon": "user-group",
        "description": "Activités sociales et amicales",
        "is_active": False
    },
    {
        "name": "Ménage",
        "color": "#6B7280",
        "icon": "home",
        "description": "Tâches ménagères et entretien",
        "is_active": False
    },
    {
        "name": "Courses",
        "color": "#10B981",
        "icon": "shopping-cart",
        "description": "Achats et commissions",
        "is_active": True
    },
    {
        "name": "Jardinage",
        "color": "#65A30D",
        "icon": "leaf",
        "description": "Entretien du jardin et plantes",
        "is_active": False
    },
    {
        "name": "Finances",
        "color": "#059669",
        "icon": "banknotes",
        "description": "Gestion financière et comptabilité",
        "is_active": False
    },
    {
        "name": "Factures",
        "color": "#DC2626",
        "icon": "receipt-tax",
        "description": "Paiements et factures à régler",
        "is_active": False
    },
    {
        "name": "Santé",
        "color": "#EF4444",
        "icon": "heart-pulse",
    }
]


# revision identifiers, used by Alembic.
revision: str = '41eda53f82ec'
down_revision: Union[str, None] = 'f2548e99db0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    for data in CATEGORIES_DATA:
        existing = session.query(Category).filter_by(name=data["name"]).first()
        if existing:
            existing.color = data["color"]
            existing.icon = data["icon"]
            existing.description = data["description"]
            existing.is_active = data["is_active"]
        else:
            session.add(Category(**data))

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)

    names = [c["name"] for c in CATEGORIES_DATA]
    session.query(Category).filter(Category.name.in_(names)).delete(synchronize_session=False)
    session.commit()
