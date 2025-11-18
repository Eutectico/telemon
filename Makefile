.PHONY: help install run docker-build docker-up docker-down logs test clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the bot locally"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start bot with Docker Compose"
	@echo "  make docker-down  - Stop bot with Docker Compose"
	@echo "  make logs         - View Docker logs"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean up generated files"

install:
	python -m venv venv
	./venv/bin/pip install -r requirements.txt

run:
	python src/main.py

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/
