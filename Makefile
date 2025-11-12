.PHONY: help install dev build test lint docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make dev         - Run development servers"
	@echo "  make build       - Build all projects"
	@echo "  make test        - Run all tests"
	@echo "  make lint        - Run linters"
	@echo "  make docker-up   - Start Docker containers"
	@echo "  make docker-down - Stop Docker containers"
	@echo "  make clean       - Clean build artifacts"

install:
	npm install
	cd frontend && npm install
	cd backend && pip install -r requirements.txt
	cd data-processing && pip install -r requirements.txt
	cd ml-services && pip install -r requirements.txt

dev:
	npm run dev

build:
	npm run build

test:
	npm run test

lint:
	npm run lint

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	rm -rf node_modules frontend/node_modules frontend/.next backend/__pycache__ backend/**/__pycache__

