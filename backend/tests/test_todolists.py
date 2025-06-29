import pytest
from fastapi import status


class TestTodoListsCRUD:
    """Tests pour les opérations CRUD des TodoLists"""
    
    def test_create_todolist_success(self, client, valid_todolist_data):
        """Test création d'une TodoList avec des données valides"""
        response = client.post("/todolists/", json=valid_todolist_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == valid_todolist_data["name"]
        assert data["id"] is not None
        assert isinstance(data["todos"], list)
        assert len(data["todos"]) == 0

    # Aucun sens fonctionnellement
    # def test_create_todolist_with_todos(self, client):
    #     """Test création d'une TodoList avec des todos initiaux"""
    #     todolist_data = {
    #         "name": "Liste avec todos",
    #         "todos": [
    #             {"name": "Todo 1", "completed": False},
    #             {"name": "Todo 2", "completed": False}
    #         ]
    #     }
        
    #     response = client.post("/todolists/", json=todolist_data)
        
    #     assert response.status_code == status.HTTP_200_OK
    #     data = response.json()
    #     assert data["name"] == todolist_data["name"]
    #     assert len(data["todos"]) == 2
        
    #     # Vérifier que les priorités sont assignées automatiquement
    #     todos = sorted(data["todos"], key=lambda x: x["priority"])
    #     assert todos[0]["priority"] == 1
    #     assert todos[1]["priority"] == 2
    
    def test_create_todolist_invalid_name(self, client):
        """Test création avec un nom invalide"""
        invalid_data = {"name": "", "todos": []}
        
        response = client.post("/todolists/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_all_todolists_empty(self, client):
        """Test récupération de toutes les TodoLists quand aucune n'existe"""
        response = client.get("/todolists/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    # multiple_todolists ?
    # def test_get_all_todolists_with_data(self, client, multiple_todolists):
    #     """Test récupération de toutes les TodoLists avec des données"""
    #     response = client.get("/todolists/")
        
    #     assert response.status_code == status.HTTP_200_OK
    #     data = response.json()
    #     assert len(data) == 3
        
    #     # Vérifier que tous les noms sont présents
    #     names = [todolist["name"] for todolist in data]
    #     assert "Liste Travail" in names
    #     assert "Liste Personnel" in names
    #     assert "Liste Courses" in names
    
    def test_get_todolist_by_id_success(self, client, sample_todolist):
        """Test récupération d'une TodoList par ID"""
        response = client.get(f"/todolists/{sample_todolist.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_todolist.id
        assert data["name"] == sample_todolist.name
    
    def test_get_todolist_by_id_not_found(self, client):
        """Test récupération d'une TodoList qui n'existe pas"""
        response = client.get("/todolists/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todolist not found"
    
    def test_update_todolist_success(self, client, sample_todolist):
        """Test mise à jour d'une TodoList"""
        update_data = {"name": "Nouveau nom", "todos": []}
        
        response = client.put(f"/todolists/{sample_todolist.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Nouveau nom"
        assert data["id"] == sample_todolist.id
    
    def test_update_todolist_not_found(self, client):
        """Test mise à jour d'une TodoList qui n'existe pas"""
        update_data = {"name": "Nouveau nom", "todos": []}
        
        response = client.put("/todolists/999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_todolist_success(self, client, sample_todolist):
        """Test suppression d'une TodoList"""
        response = client.delete(f"/todolists/{sample_todolist.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Todolist deleted successfully"
        
        # Vérifier que la TodoList n'existe plus
        get_response = client.get(f"/todolists/{sample_todolist.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_todolist_not_found(self, client):
        """Test suppression d'une Todolist qui n'existe pas"""
        response = client.delete("/todolists/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTodoListsTodos:
    """Tests pour la gestion des todos dans les TodoLists"""
    
    def test_add_todo_to_todolist_success(self, client, sample_todolist):
        """Test ajout d'un todo à une TodoList"""
        todo_data = {"name": "Nouveau todo", "completed": False}
        
        response = client.post(f"/todolists/{sample_todolist.id}/todos", json=todo_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == todo_data["name"]
        assert data["completed"] == False
        assert data["priority"] == 1  # Premier todo, priorité 1
    
    def test_add_todo_to_nonexistent_todolist(self, client):
        """Test ajout d'un todo à une TodoList qui n'existe pas"""
        todo_data = {"name": "Nouveau todo", "completed": False}
        
        response = client.post("/todolists/999/todos", json=todo_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todolist not found"
    
    def test_add_multiple_todos_priority_assignment(self, client, sample_todolist):
        """Test que les priorités sont assignées correctement lors de l'ajout de plusieurs todos"""
        todos_data = [
            {"name": "Todo 1", "completed": False},
            {"name": "Todo 2", "completed": False},
            {"name": "Todo 3", "completed": False}
        ]
        
        created_todos = []
        for todo_data in todos_data:
            response = client.post(f"/todolists/{sample_todolist.id}/todos", json=todo_data)
            assert response.status_code == status.HTTP_200_OK
            created_todos.append(response.json())
        
        # Vérifier les priorités
        assert created_todos[0]["priority"] == 1
        assert created_todos[1]["priority"] == 2
        assert created_todos[2]["priority"] == 3
    
    def test_get_todos_from_todolist_empty(self, client, sample_todolist):
        """Test récupération des todos d'une TodoList vide"""
        response = client.get(f"/todolists/{sample_todolist.id}/todos")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_todos_from_todolist_with_data(self, client, sample_todolist, sample_todos):
        """Test récupération des todos d'une TodoList avec des données"""
        response = client.get(f"/todolists/{sample_todolist.id}/todos")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        
        # Vérifier que les todos sont triés par priorité
        priorities = [todo["priority"] for todo in data]
        assert priorities == sorted(priorities)
    
    def test_get_todos_from_nonexistent_todolist(self, client):
        """Test récupération des todos d'une TodoList qui n'existe pas"""
        response = client.get("/todolists/999/todos")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todolist not found"


class TestPopulateFromLinks:
    def test_populate_from_links(self, client, db_session):
        course_cat = models.Category(name="courses", color="#000000", icon="cart")
        recipe_cat = models.Category(name="recette", color="#000000", icon="book")
        db_session.add_all([course_cat, recipe_cat])
        db_session.commit()

        course_list = models.TodoList(name="Courses", category_id=course_cat.id)
        recipe_list = models.TodoList(name="Recipe", category_id=recipe_cat.id)
        db_session.add_all([course_list, recipe_list])
        db_session.commit()

        ingredient = models.Todo(name="Tomate", completed=False, priority=1, quantity="2", todolist_id=recipe_list.id)
        db_session.add(ingredient)
        db_session.commit()

        link = models.Link(todolist_id_parent=course_list.id, todolist_id_child=recipe_list.id)
        db_session.add(link)
        db_session.commit()

        response = client.post(f"/todolists/{course_list.id}/populate_from_links")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["todos"]) == 1
        assert data["todos"][0]["name"] == "Tomate"
