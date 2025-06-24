from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.schemas import TodoCreate, Todo, TodoUpdate
from sqlalchemy import func
from app.db import models
from app.db.session import get_db
from typing import List
from sqlalchemy.exc import IntegrityError

router = APIRouter()

# ===== FONCTION HELPER POUR RECALCULER LES PRIORITÉS =====
def recalculate_priorities(db: Session, todolist_id: int):
    """Recalcule toutes les priorités d'une TodoList : actifs en premier, puis terminés"""
    
    # Récupérer tous les todos actifs (non terminés) triés par priorité
    active_todos = db.query(models.Todo).filter(
        models.Todo.todolist_id == todolist_id,
        models.Todo.completed == False
    ).order_by(models.Todo.priority.asc()).all()
    
    # Récupérer tous les todos terminés triés par priorité
    completed_todos = db.query(models.Todo).filter(
        models.Todo.todolist_id == todolist_id,
        models.Todo.completed == True
    ).order_by(models.Todo.priority.asc()).all()
    
    print(f"🔢 Recalcul pour todolist {todolist_id}:")
    print(f"   📋 Actifs: {[f'{t.id}(p:{t.priority})' for t in active_todos]}")
    print(f"   ✅ Terminés: {[f'{t.id}(p:{t.priority})' for t in completed_todos]}")
    
    
    # Renuméroter les todos actifs : 1, 2, 3...
    for index, todo in enumerate(active_todos, 1):
        old_priority = todo.priority
        todo.priority = index
        if old_priority != index:
            print(f"   🔄 Actif {todo.id}: {old_priority} → {index}")
    
    # Renuméroter les todos terminés : après les actifs
    start_priority = len(active_todos) + 1
    for index, todo in enumerate(completed_todos, start_priority):
        old_priority = todo.priority
        todo.priority = index
        if old_priority != index:
            print(f"   ✅ Terminé {todo.id}: {old_priority} → {index}")

    # flush pour forcer la synchronisation
    db.flush()
    db.commit()
    
    print(f"💾 Recalcul terminé: {len(active_todos)} actifs, {len(completed_todos)} terminés")

    return len(active_todos) + len(completed_todos)

@router.get("/", response_model=List[Todo]) 
def get_todos(db: Session = Depends(get_db)):
    """Récupérer toutes les todos"""
    return db.query(models.Todo).options(
        joinedload(models.Todo.todolist).joinedload(models.TodoList.category)
        ).order_by(models.Todo.todolist_id, models.Todo.priority).all()

@router.get("/{todolist_id}", response_model=List[Todo])
def get_todos_by_todolist(todolist_id: int, db: Session = Depends(get_db)):
    """Récupérer les todos d'une TodoList spécifique"""
    todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id).first()
    if not todolist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Todolist not found"
        )
    
    return db.query(models.Todo).filter(
        models.Todo.todolist_id == todolist_id
    ).order_by(models.Todo.priority).all()

@router.put("/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    """Mettre à jour une todo avec gestion des priorités"""
    
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Todo not found"
        )

    try:
        # Mettre à jour uniquement les champs fournis
        if todo_update.name is not None:
            db_todo.name = todo_update.name
        
        if todo_update.completed is not None:
            db_todo.completed = todo_update.completed
        
        if todo_update.priority is not None:
            # Validation de la nouvelle priorité
            if todo_update.priority < 1:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Position must be a positive number"
                )
            db_todo.priority = todo_update.priority
                
        db.commit()
        
        # Recalculer les priorités des TodoLists affectées
        recalculate_priorities(db, db_todo.todolist_id)
        
        db.refresh(db_todo)
        return db_todo
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database constraint error"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating todo"
        )

@router.delete("/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Supprimer une todo et recalculer les priorités"""
    
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    try:
        todolist_id = db_todo.todolist_id
        
        # Supprimer la todo
        db.delete(db_todo)
        db.commit()
        
        # Recalculer toutes les priorités de la TodoList
        recalculate_priorities(db, todolist_id)
        
        return {"message":  "Todo deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting todo"
        )

@router.patch("/{todo_id}/toggle", response_model=Todo)
def toggle_todo(todo_id: int, db: Session = Depends(get_db)):
    """Toggle le statut d'un todo et réorganise automatiquement les priorités"""
    
    # Récupérer le todo
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    try:
        # Toggle du statut
        was_completed = db_todo.completed
        db_todo.completed = not db_todo.completed
        
        # Commit le changement de statut d'abord
        db.commit()
        
        recalculate_priorities(db, db_todo.todolist_id)
        
        db.refresh(db_todo)
        
        return db_todo
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error toggling todo"
        )

@router.patch("/{todo_id}/move", response_model=Todo)
def move_todo_to_position(todo_id: int, new_priority: int, db: Session = Depends(get_db)):
    """Déplacer une todo à une position spécifique"""
    
    if new_priority < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Position must be a positive number"
        )
    
    db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"        
        )
    
    try:
        old_priority = db_todo.priority
        todolist_id = db_todo.todolist_id
        
        if new_priority == old_priority:
            return db_todo  # Aucun changement nécessaire
        
        # Compter le nombre total de todos dans la liste
        total_todos = db.query(func.count(models.Todo.id)).filter(
            models.Todo.todolist_id == todolist_id
        ).scalar()
        
        # Ajuster la nouvelle priorité si elle dépasse le nombre de todos
        if new_priority > total_todos:
            new_priority = total_todos
        
        # Décaler les autres todos selon le mouvement
        if new_priority < old_priority:
            # Déplacement vers le haut : décaler les todos entre new_priority et old_priority vers le bas
            db.query(models.Todo).filter(
                models.Todo.todolist_id == todolist_id,
                models.Todo.priority >= new_priority,
                models.Todo.priority < old_priority,
                models.Todo.id != todo_id
            ).update({models.Todo.priority: models.Todo.priority + 1})
        else:
            # Déplacement vers le bas : décaler les todos entre old_priority et new_priority vers le haut
            db.query(models.Todo).filter(
                models.Todo.todolist_id == todolist_id,
                models.Todo.priority > old_priority,
                models.Todo.priority <= new_priority,
                models.Todo.id != todo_id
            ).update({models.Todo.priority: models.Todo.priority - 1})
        
        # Mettre à jour la priorité de la todo
        db_todo.priority = new_priority
        
        db.commit()
        
        # Recalculer toutes les priorités pour maintenir la cohérence
        recalculate_priorities(db, todolist_id)
        
        db.refresh(db_todo)
        return db_todo
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error moving todo"
        )