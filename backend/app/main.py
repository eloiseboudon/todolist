from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import todos, todolists, categories
from app.db.session import engine
from app.db.models import Base

# Créer les tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Todo List API", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # URL de ton frontend Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todos.router, prefix="/todos", tags=["todos"])
app.include_router(todolists.router, prefix="/todolists", tags=["todolists"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])

# Route de test optionnelle
@app.get("/")
def root():
    return {"message": "Todo List API is running!"}