from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.schemas import TodoList, TodoListCreate, Todo, TodoCreate, TodoListUpdate, Link
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

@router.get("/", response_model=List[TodoList])
def get_todolists(db: Session = Depends(get_db)):
    """Récupérer toutes les TodoLists"""
    return db.query(models.TodoList).all()

@router.get("/links/all", response_model=List[Link])  
def get_all_todolist_links(db: Session = Depends(get_db)):
    """Récupérer toutes les relations entre les TodoLists"""
    return db.query(models.Link).all()


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
                    quantity=todo_data.quantity,
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
            quantity=todo.quantity,
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


@router.post("/generate_courses", response_model=TodoList)
def generate_courses(recipe_ids: List[int], db: Session = Depends(get_db)):
    """Créer une TodoList de courses à partir de listes de recettes"""

    if not recipe_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="recipe_ids required")

    # Vérifier que toutes les todolists existent et sont de type recette
    recipe_lists = (
        db.query(models.TodoList)
        .join(models.Category)
        .filter(models.TodoList.id.in_(recipe_ids))
        .filter(func.lower(models.Category.name) == "recette")
        .all()
    )

    if len(recipe_lists) != len(recipe_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Recipe list not found")

    # Obtenir ou créer la catégorie "courses"
    courses_cat = (
        db.query(models.Category)
        .filter(func.lower(models.Category.name) == "courses")
        .first()
    )
    if not courses_cat:
        courses_cat = models.Category(name="courses", color="#10B981", icon="shopping-cart")
        db.add(courses_cat)
        db.commit()
        db.refresh(courses_cat)

    # Créer la nouvelle todolist
    course_list = models.TodoList(name="Courses", category_id=courses_cat.id)
    db.add(course_list)
    db.commit()
    db.refresh(course_list)

    # Copier les ingrédients
    for rlist in recipe_lists:
        todos = db.query(models.Todo).filter(models.Todo.todolist_id == rlist.id).all()
        for todo in todos:
            new_todo = models.Todo(
                name=todo.name,
                completed=False,
                priority=9999,
                quantity=todo.quantity,
                todolist_id=course_list.id,
            )
            db.add(new_todo)
    db.commit()
    recalculate_priorities(db, course_list.id)
    db.refresh(course_list)
    return course_list

@router.get("/{todolis_id_parent}/links", response_model=List[TodoList])  
def get_all_todolist_links_by_parent(todolis_id_parent : int, db: Session = Depends(get_db)):
    """Récupérer toutes les TodoLists liées à une TodoList parent"""
    child_todolists = (
        db.query(models.TodoList)
        .join(models.Link, models.Link.todolist_id_child == models.TodoList.id)
        .filter(models.Link.todolist_id_parent == todolis_id_parent)
        .all()
    )
    if not child_todolists:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT, 
            detail=f"No child TodoLists found for parent with id {todolis_id_parent}"
        )
    return child_todolists


@router.post("/{todolist_id_parent}/add_link/{todolist_id_child}", response_model=Link)
def add_link(todolist_id_parent : int, todolist_id_child :int ,db: Session = Depends(get_db)):
    """Ajouter une relation entre deux TodoLists"""

    # Vérifier que les IDs sont différents
    if todolist_id_parent == todolist_id_child:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une TodoList ne peut pas être liée à elle-même"
        )
    
    # Vérifier que les deux TodoLists existent
    parent_todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id_parent).first()
    child_todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id_child).first()
    if not parent_todolist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent TodoList with id {todolist_id_parent} not found"
        )
    if not child_todolist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child TodoList with id {todolist_id_child} not found"
        )   
    db_link = models.Link(
        todolist_id_parent=todolist_id_parent,
        todolist_id_child=todolist_id_child
    )
    try:
        db.add(db_link)
        db.commit()
        db.refresh(db_link) 
        return db_link
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Link already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding link"
        )
   
    


@router.post("/{todolist_id}/populate_from_links", response_model=TodoList)
def populate_from_links(todolist_id: int, db: Session = Depends(get_db)):
    """Ajoute tous les todos des recettes liées à une todolist"""

    todolist = db.query(models.TodoList).filter(models.TodoList.id == todolist_id).first()
    if not todolist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todolist not found")

    linked_recipes = (
        db.query(models.TodoList)
        .join(models.Link, models.Link.todolist_id_child == models.TodoList.id)
        .filter(models.Link.todolist_id_parent == todolist_id)
        .all()
    )

    if not linked_recipes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No linked recipes found")

    for recipe in linked_recipes:
        todos = db.query(models.Todo).filter(models.Todo.todolist_id == recipe.id).all()
        for todo in todos:
            new_todo = models.Todo(
                name=todo.name,
                completed=False,
                priority=9999,
                quantity=todo.quantity,
                todolist_id=todolist_id,
            )
            db.add(new_todo)

    db.commit()
    recalculate_priorities(db, todolist_id)
    db.refresh(todolist)
    return todolist
