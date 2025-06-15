# cd Developpements/todolist-v2

dev-b:
	cd backend && make run

dev-f:
	cd frontend && npm run dev

dev:
	make dev-backend & make dev-frontend