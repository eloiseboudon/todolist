PYTHON := python3.13
VENV := venv
ACTIVATE := source $(VENV)/bin/activate

.PHONY: help venv install run clean dependencies-installed freeze migrate-init migrate-auto migrate-up migrate-down migrate-history migrate-current test test-verbose test-coverage test-watch test-unit test-integration test-file test-clean

help:
	@echo "Commandes disponibles :"
	@echo "  make venv          -> Crée l'environnement virtuel"
	@echo "  make install       -> Installe les dépendances"
	@echo "  make run           -> Lance le serveur Uvicorn"
	@echo "  make clean         -> Supprime le venv"
	@echo "  make freeze        -> Met à jour requirements.lock.txt"
	@echo "  make migrate-init  -> Initialise Alembic"
	@echo "  make migrate-auto  -> Génère une migration automatique"
	@echo "  make migrate-up    -> Applique les migrations"
	@echo "  make test          -> Lance tous les tests"
	@echo "  make test-verbose  -> Lance les tests en mode verbeux"
	@echo "  make test-coverage -> Lance les tests avec rapport de couverture"
	@echo "  make test-watch    -> Lance les tests en mode watch"
	@echo "  make test-file     -> Lance un fichier de test spécifique (file=...)"

venv:
	$(PYTHON) -m venv $(VENV)

# Fonction réutilisable pour installer les dépendances
dependencies-installed: venv
	@echo "📦 Installation des dépendances..."
	$(ACTIVATE) && $(PYTHON) -m pip install --upgrade pip --break-system-packages
	$(ACTIVATE) && $(PYTHON) -m pip install -r requirements.txt --break-system-packages
	@echo "\n✅ Dépendances installées :"
	$(ACTIVATE) && $(PYTHON) -m pip list

# Fonction réutilisable pour freeze
freeze:
	$(ACTIVATE) && $(PYTHON) -m pip freeze > requirements.lock.txt
	@echo "🔒 Fichier requirements.lock.txt mis à jour."

# Installation complète avec freeze automatique
install: dependencies-installed freeze

# Fonction réutilisable pour vérifier l'environnement
check-venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Environnement virtuel non trouvé. Lancez 'make venv' d'abord."; \
		exit 1; \
	fi

# Fonction réutilisable pour les commandes avec venv
define run-in-venv
	@$(MAKE) check-venv
	$(ACTIVATE) && $(1)
endef

run: 
	$(call run-in-venv, $(PYTHON) -m uvicorn app.main:app --reload)

create-db:
	$(call run-in-venv, $(PYTHON) create_tables.py)

clean:
	rm -rf $(VENV)
	rm -f requirements.lock.txt

# Migrations avec Alembic
migrate-init:
	$(call run-in-venv, alembic init migrations)

migrate-auto:
	@if [ -z "$(msg)" ]; then \
		echo "❌ Veuillez fournir un message: make migrate-auto msg='votre message'"; \
		exit 1; \
	fi
	$(call run-in-venv, alembic revision --autogenerate -m "$(msg)")

migrate-up:
	$(call run-in-venv, alembic upgrade head)

migrate-down:
	$(call run-in-venv, alembic downgrade -1)

migrate-history:
	$(call run-in-venv, alembic history)

migrate-current:
	$(call run-in-venv, alembic current)

# Tests
test:
	$(call run-in-venv, PYTHONPATH=. pytest)

test-verbose:
	$(call run-in-venv, PYTHONPATH=. pytest -v)

test-coverage:
	$(call run-in-venv, PYTHONPATH=. pytest --cov=app --cov-report=html --cov-report=term)

test-watch:
	$(call run-in-venv, PYTHONPATH=. pytest-watch)

test-unit:
	$(call run-in-venv, PYTHONPATH=. pytest -m unit)

test-integration:
	$(call run-in-venv, PYTHONPATH=. pytest -m integration)

test-file:
	@if [ -z "$(file)" ]; then \
		echo "❌ Veuillez spécifier un fichier: make test-file file=tests/test_example.py"; \
		exit 1; \
	fi
	$(call run-in-venv, PYTHONPATH=. pytest $(file))
	
test-clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Commandes de développement
dev: install migrate-up run

# Reset complet de l'environnement
reset: clean venv install

# Vérification de santé du projet
health-check:
	$(call run-in-venv, $(PYTHON) -c "from app.db.session import get_db; print('✅ Base de données accessible')")
	$(call run-in-venv, alembic current)
	@echo "✅ Projet en bonne santé !"

# Commandes utiles pour les tests
test-help:
	@echo "🧪 Commandes de test disponibles :"
	@echo "  make test                    -> Lance tous les tests"
	@echo "  make test-verbose            -> Tests avec sortie détaillée"
	@echo "  make test-coverage           -> Tests avec rapport de couverture"
	@echo "  make test-watch              -> Tests en mode surveillance (relance auto)"
	@echo "  make test-unit               -> Lance seulement les tests unitaires"
	@echo "  make test-integration        -> Lance seulement les tests d'intégration"
	@echo "  make test-file file=PATH     -> Lance un fichier de test spécifique"
	@echo "  make test-clean              -> Nettoie les fichiers de cache des tests"
	@echo ""
	@echo "📊 Exemples d'usage :"
	@echo "  make test-file file=tests/test_todolists.py"
	@echo "  make test-file file=tests/test_todos.py::TestTodoToggle"
	@echo "  make test-file file=tests/test_todos.py::TestTodoToggle::test_toggle_todo_active_to_completed"