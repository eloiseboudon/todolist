from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Any

class TodoBase(BaseModel):
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="Nom de la tâche"
    )
    completed: Optional[bool] = Field(
        default=False, 
        description="Statut de completion de la tâche"
    )
    priority: Optional[int] = Field(
        default=None, 
        description="Priorité de la tâche"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Le nom de la tâche ne peut pas être vide')
        
        # Nettoyer les espaces multiples et en début/fin
        cleaned = ' '.join(v.strip().split())
        
        if len(cleaned) < 1:
            raise ValueError('Le nom doit contenir au moins 1 caractère visible')
        
        if len(cleaned) > 200:
            raise ValueError('Le nom ne peut pas dépasser 200 caractères')
            
        return cleaned
    

# ✅ Pour créer un todo (via POST /todolists/{id}/todos)
class TodoCreate(TodoBase):
    # Hérite de toutes les validations de TodoBase
    pass  

# ✅ Pour mettre à jour un todo (via PUT /todos/{id}) 
class TodoUpdate(BaseModel):
    """Modèle pour mise à jour partielle d'un todo"""
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=200,
        description="Nouveau nom de la tâche"
    )
    completed: Optional[bool] = Field(
        None, 
        description="Nouveau statut de completion"
    )
    priority: Optional[int] = Field(
        None, 
        description="Nouvelle position/ordre dans la liste"
    )
    todolist_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID de la TodoList"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
            
        if not v.strip():
            raise ValueError('Le nom de la tâche ne peut pas être vide')
        
        cleaned = ' '.join(v.strip().split())
        
        if len(cleaned) < 1:
            raise ValueError('Le nom doit contenir au moins 1 caractère visible')
        
        if len(cleaned) > 200:
            raise ValueError('Le nom ne peut pas dépasser 200 caractères')
            
        return cleaned
    
    
    @field_validator('todolist_id')
    @classmethod
    def validate_todolist_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
            
        if not isinstance(v, int):
            raise ValueError('L\'ID de la TodoList doit être un nombre entier')
        
        if v <= 0:
            raise ValueError('L\'ID de la TodoList doit être un nombre positif')
        
        return v
    
    @model_validator(mode='after')
    def validate_at_least_one_field(self) -> 'TodoUpdate':
        """Vérifie qu'au moins un champ est fourni pour la mise à jour"""
        if not any([self.name, self.completed is not None, self.priority, self.todolist_id]):
            raise ValueError('Au moins un champ doit être fourni pour la mise à jour')
        return self

class Todo(TodoBase):
    """Modèle de réponse pour un Todo"""
    id: int = Field(..., gt=0, description="Identifiant unique de la tâche")

    class Config:
        from_attributes = True

class TodoListBase(BaseModel):
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Nom de la liste de tâches"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Le nom de la TodoList ne peut pas être vide')
        
        # Nettoyer les espaces multiples et en début/fin
        cleaned = ' '.join(v.strip().split())
        
        if len(cleaned) < 1:
            raise ValueError('Le nom doit contenir au moins 1 caractère visible')
        
        if len(cleaned) > 100:
            raise ValueError('Le nom ne peut pas dépasser 100 caractères')
        
        # Vérifier les caractères interdits
        forbidden_chars = ['<', '>', '"', '\'', '&', '/', '\\']
        if any(char in cleaned for char in forbidden_chars):
            raise ValueError(f'Le nom ne peut pas contenir les caractères : {", ".join(forbidden_chars)}')
            
        return cleaned

class TodoListCreate(TodoListBase):
    todos: List[TodoCreate] = Field(
        default_factory=list,
        max_length=50,
        description="Liste des tâches à créer (max 50)"
    )
    
    @field_validator('todos')
    @classmethod
    def validate_todos(cls, v: List[TodoCreate]) -> List[TodoCreate]:
        if len(v) > 50:
            raise ValueError('Une TodoList ne peut pas contenir plus de 50 tâches à la création')
        
        # Vérifier les noms de todos dupliqués
        todo_names = [todo.name.lower().strip() for todo in v if todo.name]
        if len(todo_names) != len(set(todo_names)):
            raise ValueError('Les noms de tâches ne peuvent pas être dupliqués dans la même liste')
        
        return v

class TodoListUpdate(BaseModel):
    """Modèle pour mise à jour d'une TodoList"""
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100,
        description="Nouveau nom de la liste"
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
            
        if not v.strip():
            raise ValueError('Le nom de la TodoList ne peut pas être vide')
        
        cleaned = ' '.join(v.strip().split())
        
        if len(cleaned) < 1:
            raise ValueError('Le nom doit contenir au moins 1 caractère visible')
        
        if len(cleaned) > 100:
            raise ValueError('Le nom ne peut pas dépasser 100 caractères')
        
        forbidden_chars = ['<', '>', '"', '\'', '&', '/', '\\']
        if any(char in cleaned for char in forbidden_chars):
            raise ValueError(f'Le nom ne peut pas contenir les caractères : {", ".join(forbidden_chars)}')
            
        return cleaned

class TodoList(TodoListBase):
    """Modèle de réponse pour une TodoList"""
    id: int = Field(..., gt=0, description="Identifiant unique de la liste")
    todos: List[Todo] = Field(
        default_factory=list,
        description="Liste des tâches"
    )

    class Config:
        from_attributes = True

# ===== MODÈLES POUR LES STATISTIQUES ET FILTRES =====

class TodoStats(BaseModel):
    """Statistiques d'une TodoList"""
    total_todos: int = Field(..., ge=0)
    completed_todos: int = Field(..., ge=0)
    pending_todos: int = Field(..., ge=0)
    completion_rate: float = Field(..., ge=0.0, le=100.0)
    priority_distribution: dict[int, int] = Field(default_factory=dict)

class TodoFilter(BaseModel):
    """Filtres pour la recherche de todos"""
    completed: Optional[bool] = Field(None, description="Filtrer par statut de completion")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Filtrer par priorité")
    search: Optional[str] = Field(None, max_length=100, description="Recherche dans le nom")
    
    @field_validator('search')
    @classmethod
    def validate_search(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        
        # Nettoyer la recherche
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError('La recherche doit contenir au moins 2 caractères')
        
        return cleaned
    
    
# Categories 

class CategoryBase(BaseModel):
    id: int = Field(..., gt=0, description="Identifiant unique de la liste")
    name: str = Field(
        default="Nom de la catégorie", 
        description="Nom de la catégorie"
    )
    color: str = Field(
        default="#3B82F6", 
        description="Couleur de la catégorie"
    )
    icone: str = Field(
        default="/icones/categories", 
        description="Icone de la catégorie"
    )
    
class CategoryCreate(CategoryBase):
# Hérite de toutes les validations de CategoryCreate
    pass  