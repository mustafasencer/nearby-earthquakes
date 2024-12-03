.PHONY: dev-deps deps format lint build-docker run-docker run-cli test test-with-coverage help
.DEFAULT_GOAL := help

SERVICE=nearby-earthquakes
IMAGE=$(SERVICE):latest

## dev-deps: Install python dev packages
dev-deps:
	pip install -r requirements.dev.txt

## deps: Install python packages
deps:
	pip install -r requirements.txt

## format: Format codebase
format:
	autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place tests main.py --exclude=__init__.py
	black tests main.py
	isort tests main.py --profile black

## lint: Lint codebase
lint:
	mypy main.py
	black tests main.py --check
	isort tests main.py --check-only --profile black

## build-docker: Build Docker image
build-docker:
	docker build . -t $(IMAGE)

## build: Build Docker image
run-docker:
	docker run $(IMAGE)

## run-cli: Play game via CLI
run-cli:
	python main.py

## test: Run the project unit tests
test:
	pytest -v

## test-with-coverage: Run the unit tests and calculate the coverage
test-with-coverage:
	pytest --cov-report term-missing --cov=.

## :
## help: Print out available make targets.
help: Makefile
	@echo
	@echo " Choose a command run:"
	@echo
	@sed -n 's/^##//p' $< | column -t -s ':' |  sed -e 's/^/ /'
	@echo