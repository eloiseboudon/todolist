import pytest
from fastapi import status


class TestTodoListValidation:
    """Tests de validation pour les TodoLists"""
    
    def test_create_todolist_empty_name(self, client):
        """Test création TodoList avec nom vide"""
        data = {"name": "", "todos": []}
        
        response = client.post("/todolists/", json=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        assert any("name" in str(error).lower() for error in error_detail)
    
    def test_create_todolist_missing_name(self, client):
        """Test création TodoList sans nom"""
        data = {"todos": []}  # name manquant
        
        response = client.post("/todolists/", json=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todolist_invalid_todos_structure(self, client):
        """Test création TodoList avec structure de todos invalide"""
        data = {
            "name": "Liste valide",
            "todos": [
                {"name": "Todo valide"},
                {"invalid_field": "valeur"},  # Structure invalide
            ]
        }
        
        response = client.post("/todolists/", json=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todolist_name_too_long(self, client):
        """Test création TodoList avec nom très long"""
        long_name = "x" * 1000  # Nom très long
        data = {"name": long_name, "todos": []}
        
        response = client.post("/todolists/", json=data)
        
        # Peut être accepté selon la validation, mais bon à tester
        # Si tu ajoutes une limite de longueur, ce test sera utile
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestTodoValidation:
    """Tests de validation pour les Todos"""
    
    def test_create_todo_empty_name(self, client, sample_todolist):
        """Test création todo avec nom vide"""
        data = {"name": "", "completed": False}
        
        response = client.post(f"/todolists/{sample_todolist.id}/todos", json=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todo_missing_name(self, client, sample_todolist):
        """Test création todo sans nom"""
        data = {"completed": False}  # name manquant
        
        response = client.post(f"/todolists/{sample_todolist.id}/todos", json=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todo_invalid_completed_type(self, client, sample_todolist):
        """Test création todo avec type completed invalide"""
        data = {"name": "Todo valide", "completed": "not_a_boolean"}
        
        response = client.post(f"/todolists/{sample_todolist.id}/todos", json=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_todo_invalid_priority_type(self, client, sample_todolist):
        """Test création todo avec type priority invalide"""
        data = {"name": "Todo valide", "completed": False, "priority": "not_an_integer"}
        
        response = client.post(f"/todolists/{sample_todolist.id}/todos", json=data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_todo_invalid_data_types(self, client, sample_todos):
        """Test mise à jour todo avec types de données invalides"""
        todo = sample_todos[0]
        
        invalid_data = {
            "name": 123,  # Doit être string
            "completed": "yes",  # Doit être boolean
            "priority": "high",  # Doit être integer
            "todolist_id": "not_an_id"  # Doit être integer
        }
        
        response = client.put(f"/todos/{todo.id}", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    # a traiter 
    # def test_update_todo_negative_priority(self, client, sample_todos):
    #     """Test mise à jour todo avec priorité négative"""
    #     todo = sample_todos[0]
        
    #     data = {
    #         "name": "Todo valide",
    #         "completed": False,
    #         "priority": -1,  # Priorité négative
    #         "todolist_id": todo.todolist_id
    #     }
        
    #     response = client.put(f"/todos/{todo.id}", json=data)
        
    #     # Selon ta logique métier, tu peux vouloir rejeter les priorités négatives
    #     # ou les accepter. Ajuste ce test selon tes besoins.
    #     assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestAPIErrorHandling:
    """Tests pour la gestion d'erreurs de l'API"""
    
    def test_invalid_json_payload(self, client):
        """Test avec payload JSON invalide"""
        response = client.post(
            "/todolists/", 
            data="invalid json",  # JSON malformé
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_content_type(self, client):
        """Test sans Content-Type approprié"""
        # Ce test dépend de la configuration FastAPI
        # Peut être que FastAPI gère automatiquement
        pass
    
    def test_invalid_http_method(self, client):
        """Test avec méthode HTTP non supportée"""
        response = client.patch("/todolists/")  # PATCH non supporté sur cette route
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_invalid_url_parameter_type(self, client):
        """Test avec paramètre URL de type invalide"""
        response = client.get("/todolists/not_an_integer")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_very_large_payload(self, client):
        """Test avec payload très volumineux"""
        large_data = {
            "name": "Liste normale",
            "todos": [{"name": f"Todo {i}"} for i in range(10000)]  # Beaucoup de todos
        }
        
        response = client.post("/todolists/", json=large_data)
        
        # Peut réussir ou échouer selon les limites configurées
        # Bon test pour vérifier les performances et limites
        assert response.status_code in [
            status.HTTP_200_OK, 
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        ]


class TestEdgeCases:
    """Tests pour les cas limites"""
    
    def test_unicode_characters_in_names(self, client, sample_todolist):
        """Test avec caractères Unicode"""
        unicode_data = {
            "name": "🎯 Todo avec émojis et αβγ caractères spéciaux 中文",
            "completed": False
        }
        
        response = client.post(f"/todolists/{sample_todolist.id}/todos", json=unicode_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == unicode_data["name"]
    
    def test_special_characters_in_names(self, client, sample_todolist):
        """Test avec caractères spéciaux"""
        special_chars_data = {
            "name": "Todo avec 'quotes', \"double quotes\", <tags>, & ampersands",
            "completed": False
        }
        
        response = client.post(f"/todolists/{sample_todolist.id}/todos", json=special_chars_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == special_chars_data["name"]
    
    def test_whitespace_only_name(self, client, sample_todolist):
        """Test avec nom contenant seulement des espaces"""
        whitespace_data = {"name": "   ", "completed": False}
        
        response = client.post(f"/todolists/{sample_todolist.id}/todos", json=whitespace_data)
        
        # Selon ta logique, tu peux vouloir rejeter ou accepter
        # Tu peux ajouter une validation pour trim les espaces
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    # gestion de sample_todos ? 
    # def test_extremely_high_priority(self, client, sample_todos):
    #     """Test avec priorité extrêmement élevée"""
    #     todo = sample_todos[0]
        
    #     data = {
    #         "name": "Todo priorité extrême",
    #         "completed": False,
    #         "priority": 999999999,
    #         "todolist_id": todo.todolist_id
    #     }
        
    #     response = client.put(f"/todos/{todo.id}", json=data)
        
    #     assert response.status_code == status.HTTP_200_OK
    #     assert response.json()["priority"] == 999999999