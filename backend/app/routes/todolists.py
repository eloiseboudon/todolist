from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.schemas import TodoList, TodoListCreate, Todo, TodoCreate, TodoListUpdate
from app.db import models
from app.db.session import get_db
from typing import List, Optional
from sqlalchemy.exc import IntegrityError

router = APIRouter()

def recalculate_priorities(db: Session, todolist_id: int):
    """Recalcule toutes les priorités d'une TodoList : actifs en premier, puis terminés"""
    
    # Récupérer tous les todos actifs (non terminés) triés par priorité
    active_todos = db.query(models.Todo).filter(
        models.Todo.todolist_id == todolist_id,
        models.Todo.completed == False
    ).order_by(models.Todo.priority.asc(),
            models.Todo.created_at.desc()).all()
    
    # Récupérer tous les todos terminés triés par priorité
    completed_todos = db.query(models.Todo).filter(
        models.Todo.todolist_id == todolist_id,
        models.Todo.completed == True
    ).order_by(models.Todo.priority.asc(),
            models.Todo.created_at.desc()).all()
    
    # Renuméroter les todos actifs : 1, 2, 3...
    for index, todo in enumerate(active_todos, 1):
        todo.priority = index
    
    # Renuméroter les todos terminés : après les actifs
    start_priority = len(active_todos) + 1
    for index, todo in enumerate(completed_todos, start_priority):
        todo.priority = index
    
    db.commit()
    return len(active_todos) + len(completed_todos)

@router.post("/", response_model=TodoList)
def create_todolist(todolist: TodoListCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle TodoList avec todos optionnels"""
    try:
        # Créer la todolist
        db_todolist = models.TodoList(name=todolist.name)
        
        if todolist.category_id is not None:
            db_todolist.category_id = todolist.category_id

        db.add(db_todolist)
        db.commit()
        db.refresh(db_todolist)

        # Ajouter les todos si fournis
        if todolist.todos:
            for index, todo_data in enumerate(todolist.todos, 1):
                # Assigner les priorités automatiquement : 1, 2, 3...
                final_priority = todo_data.priority if todo_data.priority is not None else index
                
                db_todo = models.Todo(
                    name=todo_data.name,
                    completed=todo_data.completed,
                    priority=final_priority,
                    todolist_id=db_todolist.id
                )
                db.add(db_todo)
            
            db.commit()
            
            # Recalculer les priorités pour s'assurer de la cohérence
            recalculate_priorities(db, db_todolist.id)
            db.refresh(db_todolist)
        
        return db_todolist
        
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
            detail="Error creating TodoList"
        )

@router.get("/", response_model=List[TodoList])
def get_todolists(db: Session = Depends(get_db)):
    """Récupérer toutes les TodoLists"""
    return db.query(models.TodoList).all()

@router.get("/{todolist_id}", response_model=TodoList)  
def get_todolist(todolist_id: int, db: Session = Depends(get_db)):
    """Récupérer une TodoList par ID"""
    todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id).first()
    if not todolist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Todolist not found"
        )
    return todolist

@router.put("/{todolist_id}", response_model=TodoList)
def update_todolist(todolist_id: int, todolist_update: TodoListUpdate, db: Session = Depends(get_db)):
    """Mettre à jour une TodoList"""
    db_todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id).first()
    if not db_todolist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="TodoList not found"
        )
    
    try:
        # Mettre à jour uniquement les champs fournis
        if todolist_update.name is not None:
            db_todolist.name = todolist_update.name
        
        if todolist_update.category_id is not None:
            db_todolist.category_id = todolist_update.category_id
        
        db.commit()
        db.refresh(db_todolist)
        return db_todolist
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A todoList with this name already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating todolist"
        )
@router.post("/{todolist_id}/todos", response_model=Todo)
def add_todo_to_list(todolist_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    """Ajouter une nouvelle todo à une TodoList"""
    
    # Vérifier que la todolist existe
    todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id).first()
    if not todolist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="TodoList not found"        
        )
    
    try:
        # Si priorité fournie on l'applique, sinon la todo sera la dernère de la liste, recalculate_priorities() rénumérotera
        if todo.priority is not None and todo.priority > 0:
            temp_priority = todo.priority
        else :
            temp_priority = 9999
                   
        # Créer la todo avec une priorité temporaire
        db_todo = models.Todo(
            name=todo.name,
            completed=todo.completed,  # Normalement False
            priority=temp_priority,
            todolist_id=todolist_id
        )

        db.add(db_todo)
        db.commit()
        
        recalculate_priorities(db, todolist_id)
        
        db.refresh(db_todo)
        
        print(f"✅ Todo créée et priorité recalculée: {db_todo.priority}")
        
        return db_todo

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de l'ajout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating todo"
        )

@router.put("/{todolist_id}/todos/reorder")
def reorder_todos(todolist_id: int, todo_ids: List[int], db: Session = Depends(get_db)):
    """Réorganise les todos selon l'ordre fourni"""
    
    # Vérifier que la todolist existe
    todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id).first()
    if not todolist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todolist not found"
        )
    
    try:
        # Vérifier que tous les todo_ids existent dans cette todolist
        existing_todos = db.query(models.Todo).filter(
            models.Todo.id.in_(todo_ids),
            models.Todo.todolist_id == todolist_id
        ).all()
        
        if len(existing_todos) != len(todo_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todos doesn't exist in this todolist"
            )
        
        # Réorganiser selon l'ordre fourni
        for index, todo_id in enumerate(todo_ids, 1):
            db.query(models.Todo).filter(
                models.Todo.id == todo_id,
                models.Todo.todolist_id == todolist_id
            ).update({"priority": index})
        
        # flush pour forcer la synchronisation
        db.flush()
        db.commit()
        
        # Recalculer toutes les priorités pour maintenir la cohérence
        recalculate_priorities(db, todolist_id)
        
        return {"message": "Todos reordered successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reordering todos"
        )

@router.delete("/{todolist_id}")
def delete_todolist(todolist_id: int, db: Session = Depends(get_db)):
    """Supprimer une TodoList et toutes ses todos"""
    db_todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id).first()
    if not db_todolist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todolist not found"
        )
    
    try:
        db.delete(db_todolist)
        db.commit()
        return {"message": "Todolist deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting todolist"
        )

@router.get("/{todolist_id}/todos", response_model=List[Todo])
def get_todos_from_list(
    todolist_id: int, 
    completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Récupérer les todos d'une TodoList avec filtre optionnel"""
    todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id).first()
    if not todolist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todolist not found"
        )
    
    query = db.query(models.Todo).filter(models.Todo.todolist_id == todolist_id)
    
    # Filtre optionnel par statut
    if completed is not None:
        query = query.filter(models.Todo.completed == completed)
    
    return query.order_by(models.Todo.priority).all()