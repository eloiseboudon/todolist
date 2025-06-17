from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship


class TodoList(Base): 
    __tablename__ = "todolist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    todos = relationship("Todo", back_populates="todolist", cascade="all, delete-orphan")


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    todolist_id = Column(Integer, ForeignKey("todolist.id"))
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("category.id"))
    todolist = relationship("TodoList", back_populates="todos")
    category = relationship("Category",back_populates="category")

class Category(Base):
    __tablename__ = "category"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    color = Column(String, default="#3B82F6")
    icon = Column(String, nullable=True)

