import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.db.models import Base
from app.db import models

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Crée une nouvelle session de base de données pour chaque test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function") 
def client(db_session):
    """Client de test FastAPI avec base de données de test"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_todolist(db_session):
    """Crée une TodoList de test"""
    todolist = models.TodoList(name="Test TodoList")
    db_session.add(todolist)
    db_session.commit()
    db_session.refresh(todolist)
    return todolist

@pytest.fixture
def sample_todo(db_session, sample_todolist):
    """Crée un Todo de test"""
    todo = models.Todo(
        name="Test Todo",
        completed=False,
        priority=1,
        todolist_id=sample_todolist.id
    )
    db_session.add(todo)
    db_session.commit()
    db_session.refresh(todo)
    return todo

@pytest.fixture
def sample_todos(db_session, sample_todolist):
    """Crée plusieurs Todos de test"""
    todos = [
        models.Todo(name="Todo 1", completed=False, priority=1, todolist_id=sample_todolist.id),
        models.Todo(name="Todo 2", completed=False, priority=2, todolist_id=sample_todolist.id),
        models.Todo(name="Todo 3", completed=True, priority=3, todolist_id=sample_todolist.id),
    ]
    
    for todo in todos:
        db_session.add(todo)
    
    db_session.commit()
    
    for todo in todos:
        db_session.refresh(todo)
    
    return todos

@pytest.fixture
def multiple_todolists(db_session):
    """Crée plusieurs TodoLists de test"""
    todolists = [
        models.TodoList(name="Work"),
        models.TodoList(name="Personal"),
        models.TodoList(name="Shopping"),
    ]
    
    for todolist in todolists:
        db_session.add(todolist)
    
    db_session.commit()
    
    for todolist in todolists:
        db_session.refresh(todolist)
    
    return todolists

@pytest.fixture
def complex_scenario(db_session):
    """Scénario complexe avec plusieurs TodoLists et Todos"""
    # TodoList 1 avec todos mixtes
    todolist1 = models.TodoList(name="Work Tasks")
    db_session.add(todolist1)
    db_session.commit()
    db_session.refresh(todolist1)
    
    work_todos = [
        models.Todo(name="Meeting prep", completed=False, priority=1, todolist_id=todolist1.id),
        models.Todo(name="Write report", completed=False, priority=2, todolist_id=todolist1.id),
        models.Todo(name="Review code", completed=True, priority=3, todolist_id=todolist1.id),
        models.Todo(name="Send emails", completed=True, priority=4, todolist_id=todolist1.id),
    ]
    
    # TodoList 2 avec tous les todos terminés
    todolist2 = models.TodoList(name="Completed Tasks")
    db_session.add(todolist2)
    db_session.commit()
    db_session.refresh(todolist2)
    
    completed_todos = [
        models.Todo(name="Task A", completed=True, priority=1, todolist_id=todolist2.id),
        models.Todo(name="Task B", completed=True, priority=2, todolist_id=todolist2.id),
    ]
    
    all_todos = work_todos + completed_todos
    for todo in all_todos:
        db_session.add(todo)
    
    db_session.commit()
    
    for todo in all_todos:
        db_session.refresh(todo)
    
    return {
        "work_todolist": todolist1,
        "completed_todolist": todolist2,
        "work_todos": work_todos,
        "completed_todos": completed_todos,
        "all_todos": all_todos
    }

# ===== FIXTURES AJOUTÉES POUR LES TESTS MANQUANTS =====

@pytest.fixture
def valid_todolist_data():
    """Données valides pour créer une TodoList"""
    return {
        "name": "Ma nouvelle TodoList"
    }

@pytest.fixture
def invalid_todolist_data():
    """Données invalides pour tester les erreurs"""
    return {
        "name": ""  # Nom vide
    }

@pytest.fixture
def complex_todolist_with_todos(db_session):
    """TodoList complexe avec plusieurs todos pour les tests de toggle"""
    # Créer une TodoList
    todolist = models.TodoList(name="Complex TodoList")
    db_session.add(todolist)
    db_session.commit()
    db_session.refresh(todolist)
    
    # Créer des todos avec différents statuts
    todos = [
        models.Todo(name="Active Todo 1", completed=False, priority=1, todolist_id=todolist.id),
        models.Todo(name="Active Todo 2", completed=False, priority=2, todolist_id=todolist.id),
        models.Todo(name="Completed Todo 1", completed=True, priority=3, todolist_id=todolist.id),
        models.Todo(name="Completed Todo 2", completed=True, priority=4, todolist_id=todolist.id),
    ]
    
    for todo in todos:
        db_session.add(todo)
    
    db_session.commit()
    
    for todo in todos:
        db_session.refresh(todo)
    
    return {
        "todolist": todolist,
        "todos": todos,
        "active_todos": [t for t in todos if not t.completed],
        "completed_todos": [t for t in todos if t.completed]
    }

@pytest.fixture
def valid_todo_data(sample_todolist):
    """Données valides pour créer un Todo"""
    return {
        "name": "Nouvelle tâche",
        "completed": False,
        "priority": 1,
        "todolist_id": sample_todolist.id
    }

@pytest.fixture
def invalid_todo_data():
    """Données invalides pour tester les erreurs"""
    return {
        "name": "",  # Nom vide
        "completed": False,
        "priority": 1,
        "todolist_id": 999  # ID inexistant
    }

@pytest.fixture
def todolist_with_mixed_todos(db_session):
    """TodoList avec un mélange de todos actifs/complétés pour tests génériques"""
    todolist = models.TodoList(name="Mixed TodoList")
    db_session.add(todolist)
    db_session.commit()
    db_session.refresh(todolist)
    
    todos = [
        models.Todo(name="Active high priority", completed=False, priority=1, todolist_id=todolist.id),
        models.Todo(name="Active medium priority", completed=False, priority=2, todolist_id=todolist.id),
        models.Todo(name="Active low priority", completed=False, priority=3, todolist_id=todolist.id),
        models.Todo(name="Completed high priority", completed=True, priority=1, todolist_id=todolist.id),
        models.Todo(name="Completed medium priority", completed=True, priority=2, todolist_id=todolist.id),
    ]
    
    for todo in todos:
        db_session.add(todo)
    
    db_session.commit()
    
    for todo in todos:
        db_session.refresh(todo)
    
    return {
        "todolist": todolist,
        "all_todos": todos,
        "active_todos": [t for t in todos if not t.completed],
        "completed_todos": [t for t in todos if t.completed],
        "high_priority_todos": [t for t in todos if t.priority == 1],
        "medium_priority_todos": [t for t in todos if t.priority == 2],
        "low_priority_todos": [t for t in todos if t.priority == 3]
    }

@pytest.fixture
def empty_todolist(db_session):
    """TodoList vide pour tester les cas limites"""
    todolist = models.TodoList(name="Empty TodoList")
    db_session.add(todolist)
    db_session.commit()
    db_session.refresh(todolist)
    return todolist