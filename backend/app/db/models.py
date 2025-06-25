from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship


class TodoList(Base): 
    __tablename__ = "todolist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    todos = relationship("Todo", back_populates="todolist", cascade="all, delete-orphan")
    category = relationship("Category", back_populates="todolist")
    
    # Foreign Keys
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), nullable=False)  # Format #RRGGBB
    icon = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    todolist = relationship("TodoList", back_populates="category")

    def __repr__(self):
        return f"<Category(name='{self.name}', color='{self.color}')>"


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    description = Column(String, nullable=True)
    quantity = Column(String, nullable=True)
    
    # Foreign Keys
    todolist_id = Column(Integer, ForeignKey("todolist.id"), nullable=False)
    
    # Relations
    todolist = relationship("TodoList", back_populates="todos")

    def __repr__(self):
        return f"<Todo(name='{self.name}', completed={self.completed})>"

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    todolist_id_parent = Column(Integer, ForeignKey("todolist.id"), nullable=False)
    todolist_id_child = Column(Integer, ForeignKey("todolist.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relations
    parent_todolist = relationship("TodoList", foreign_keys=[todolist_id_parent])
    child_todolist = relationship("TodoList", foreign_keys=[todolist_id_child])
    
    # Contrainte d'unicité pour éviter les doublons
    __table_args__ = (
        UniqueConstraint('todolist_id_parent', 'todolist_id_child', name='unique_parent_child_link'),
        CheckConstraint('todolist_id_parent != todolist_id_child', name='prevent_self_link')
    )