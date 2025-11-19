.PHONY: up down build shell-api shell-worker migrate makemigrations test

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

shell-api:
	docker compose exec api bash

shell-worker:
	docker compose exec worker bash

migrate:
	docker compose exec api bash -lc "python manage.py migrate"

makemigrations:
	docker compose exec api bash -lc "python manage.py makemigrations"

test:
	docker compose exec api bash -lc "pytest"


