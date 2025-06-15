import pytest
from fastapi import status


class TestTodosCRUD:
    """Tests pour les opérations CRUD des Todos"""
    
    def test_get_all_todos_empty(self, client):
        """Test récupération de tous les todos quand aucun n'existe"""
        response = client.get("/todos/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
    
    def test_get_all_todos_with_data(self, client, sample_todos):
        """Test récupération de tous les todos avec des données"""
        response = client.get("/todos/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3  # Au moins les 3 todos de sample_todos
        
    # à faire
    # def test_update_todo_success(self, client, sample_todos):
    #     """Test mise à jour d'un todo"""
    #     todo = sample_todos[0]
    #     update_data = {
    #         "name": "Todo modifié",
    #         "completed": True,
    #         "priority": 5,
    #         "todolist_id": todo.todolist_id
    #     }
        
    #     response = client.put(f"/todos/{todo.id}", json=update_data)
        
    #     assert response.status_code == status.HTTP_200_OK
    #     data = response.json()
    #     assert data["name"] == "Todo modifié"
    #     assert data["completed"] == True
    #     assert data["priority"] == 5
    #     assert data["id"] == todo.id
    
    def test_update_todo_name(self, client,sample_todos):
        """Test mise à jour d'un nom d'un todo"""
        todo = sample_todos[0]
        update_data = {
            "name": "Nouveau nom",
            "completed": todo.completed,
            "priority": todo.priority
        }
        
        response = client.put(f"/todos/{todo.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Nouveau nom"

    def test_update_todo_not_found(self, client):
        """Test mise à jour d'un todo qui n'existe pas"""
        update_data = {
            "name": "Todo inexistant",
            "completed": False,
            "priority": 1
        }
        
        response = client.put("/todos/999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todo not found"
    
    def test_delete_todo_success(self, client, sample_todos):
        """Test suppression d'un todo"""
        todo = sample_todos[0]
        
        response = client.delete(f"/todos/{todo.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "Todo deleted successfully"
        
        # Vérifier que le todo n'existe plus
        update_response = client.put(f"/todos/{todo.id}", json={
            "name": "Test", "completed": False, "priority": 1, "todolist_id": 1
        })
        assert update_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_todo_not_found(self, client):
        """Test suppression d'un todo qui n'existe pas"""
        response = client.delete("/todos/999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todo not found"


class TestTodoToggle:
    """Tests pour la fonctionnalité de toggle des todos"""
    
    def test_toggle_todo_active_to_completed(self, client, complex_todolist_with_todos):
        """Test toggle d'un todo actif vers terminé"""
        todos = complex_todolist_with_todos["todos"]
        active_todo = complex_todolist_with_todos["active_todos"][0]
        initial_priority = active_todo.priority
        
        response = client.patch(f"/todos/{active_todo.id}/toggle")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] == True
        assert data["id"] == active_todo.id
        # La priorité peut changer selon la logique de renumérotation
    
    def test_toggle_todo_completed_to_active(self, client, complex_todolist_with_todos):
        """Test toggle d'un todo terminé vers actif"""
        completed_todo = complex_todolist_with_todos["completed_todos"][0]
        
        response = client.patch(f"/todos/{completed_todo.id}/toggle")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] == False
        assert data["id"] == completed_todo.id
    
    def test_toggle_todo_not_found(self, client):
        """Test toggle d'un todo qui n'existe pas"""
        response = client.patch("/todos/999/toggle")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Todo not found"
    
    def test_toggle_multiple_todos_priority_management(self, client, sample_todolist):
        """Test que les priorités sont correctement gérées lors de multiples toggles"""
        # Créer 3 todos actifs
        todos_data = [
            {"name": "Todo A", "completed": False},
            {"name": "Todo B", "completed": False},
            {"name": "Todo C", "completed": False}
        ]
        
        created_todos = []
        for todo_data in todos_data:
            response = client.post(f"/todolists/{sample_todolist.id}/todos", json=todo_data)
            created_todos.append(response.json())
        
        # Toggle le todo du milieu (Todo B, priorité 2)
        response = client.patch(f"/todos/{created_todos[1]['id']}/toggle")
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier l'état final de tous les todos
        get_response = client.get(f"/todolists/{sample_todolist.id}/todos")
        final_todos = get_response.json()
        
        # Séparer actifs et terminés
        active_todos = [t for t in final_todos if not t["completed"]]
        completed_todos = [t for t in final_todos if t["completed"]]
        
        # Vérifier que les priorités sont continues
        active_priorities = [t["priority"] for t in active_todos]
        assert len(active_todos) == 2
        assert sorted(active_priorities) == list(range(1, len(active_todos) + 1))
        
        # Le todo terminé doit avoir une priorité après les actifs
        assert len(completed_todos) == 1
        assert completed_todos[0]["priority"] > max(active_priorities)


class TestTodoPriorityManagement:
    """Tests pour la gestion automatique des priorités"""
    # sample_todolist, sample_todos ?
    # def test_new_todo_gets_correct_priority(self, client, sample_todolist, sample_todos):
    #     """Test qu'un nouveau todo reçoit la bonne priorité"""
    #     # Les sample_todos contiennent des todos avec priorités 1, 2, 3
    #     # Le nouveau todo doit avoir la priorité suivante parmi les actifs
        
    #     # Compter les todos actifs existants
    #     active_count = len([t for t in sample_todos if not t.completed])
        
    #     todo_data = {"name": "Nouveau todo", "completed": False}
    #     response = client.post(f"/todolists/{sample_todolist.id}/todos", json=todo_data)
        
    #     assert response.status_code == status.HTTP_200_OK
    #     data = response.json()
    #     expected_priority = active_count + 1
    #     assert data["priority"] == expected_priority
    
    def test_priority_renumbering_after_toggle(self, client, sample_todolist):
        """Test que les priorités sont renumérotées après un toggle"""
        # Créer 4 todos : 3 actifs + 1 terminé
        todos_data = [
            {"name": "Todo 1", "completed": False},  # priorité 1
            {"name": "Todo 2", "completed": False},  # priorité 2
            {"name": "Todo 3", "completed": False},  # priorité 3
        ]
        
        created_todos = []
        for todo_data in todos_data:
            response = client.post(f"/todolists/{sample_todolist.id}/todos", json=todo_data)
            created_todos.append(response.json())
        
        # Toggle le premier todo (priorité 1)
        response = client.patch(f"/todos/{created_todos[0]['id']}/toggle")
        assert response.status_code == status.HTTP_200_OK
        
        # Récupérer l'état final
        get_response = client.get(f"/todolists/{sample_todolist.id}/todos")
        final_todos = get_response.json()
        
        # Vérifier que les priorités sont continues et commencent à 1
        active_todos = sorted([t for t in final_todos if not t["completed"]], 
                            key=lambda x: x["priority"])
        completed_todos = sorted([t for t in final_todos if t["completed"]], 
                               key=lambda x: x["priority"])
        
        # Les todos actifs doivent avoir les priorités 1, 2
        assert len(active_todos) == 2
        assert [t["priority"] for t in active_todos] == [1, 2]
        
        # Le todo terminé doit avoir une priorité après les actifs
        assert len(completed_todos) == 1
        assert completed_todos[0]["priority"] == 3
    
    def test_empty_todolist_first_todo_priority_one(self, client, sample_todolist):
        """Test que le premier todo d'une liste vide a la priorité 1"""
        todo_data = {"name": "Premier todo", "completed": False}
        
        response = client.post(f"/todolists/{sample_todolist.id}/todos", json=todo_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["priority"] == 1
    
    # sample_todolist ?
    # def test_priority_consistency_after_multiple_operations(self, client, sample_todolist):
    #     """Test de cohérence des priorités après plusieurs opérations"""
    #     # Scénario complexe : créer, toggle, créer, toggle, créer
        
    #     # 1. Créer 2 todos
    #     todo1_response = client.post(f"/todolists/{sample_todolist.id}/todos", 
    #                                json={"name": "Todo 1", "completed": False})
    #     todo2_response = client.post(f"/todolists/{sample_todolist.id}/todos", 
    #                                json={"name": "Todo 2", "completed": False})
        
    #     todo1_id = todo1_response.json()["id"]
    #     todo2_id = todo2_response.json()["id"]
        
    #     # 2. Toggle le premier
    #     client.patch(f"/todos/{todo1_id}/toggle")
        
    #     # 3. Créer un troisième todo
    #     todo3_response = client.post(f"/todolists/{sample_todolist.id}/todos", 
    #                                json={"name": "Todo 3", "completed": False})
    #     todo3_id = todo3_response.json()["id"]
        
    #     # 4. Toggle le deuxième
    #     client.patch(f"/todos/{todo2_id}/toggle")
        
    #     # 5. Créer un quatrième todo
    #     todo4_response = client.post(f"/todolists/{sample_todolist.id}/todos", 
    #                                json={"name": "Todo 4", "completed": False})
        
    #     # Vérifier l'état final
    #     get_response = client.get(f"/todolists/{sample_todolist.id}/todos")
    #     final_todos = get_response.json()
        
    #     active_todos = sorted([t for t in final_todos if not t["completed"]], 
    #                         key=lambda x: x["priority"])
    #     completed_todos = sorted([t for t in final_todos if t["completed"]], 
    #                            key=lambda x: x["priority"])
        
    #     # Doit y avoir 2 actifs avec priorités 1, 2
    #     assert len(active_todos) == 2
    #     assert [t["priority"] for t in active_todos] == [1, 2]
        
    #     # Doit y avoir 2 terminés avec priorités 3, 4
    #     assert len(completed_todos) == 2
    #     assert [t["priority"] for t in completed_todos] == [3, 4]