run:
	source ./venv/bin/activate && uvicorn --reload temperature_monitor_api.routes.base:app

db:
	docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust --name db-temperature_monitor_api postgres:15
	sleep 3

migrate:
	alembic upgrade head
