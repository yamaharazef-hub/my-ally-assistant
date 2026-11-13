VERSION := 1.0.0

.PHONY: install run test lint autopep8 build_docker run_docker clean

install: ## Run the interactive installer (creates env/ and the ally launcher)
	python3 installer

run: ## Start My Ally Assistant
	@if [ -f env/bin/activate ]; then . env/bin/activate; fi; \
	python3 allycli

test: ## Run the unit test suite
	@if [ -f env/bin/activate ]; then . env/bin/activate; fi; \
	cd allycli && python3 -m unittest discover

lint: ## Check code style with flake8
	flake8 --select E,W --max-line-length=140 --ignore E722,W503,W504,E128 allycli/ installer

autopep8: ## Auto-format the codebase
	@find . -iname "*.py" -not -path "./env/**" | xargs autopep8 --in-place --aggressive --aggressive --max-line-length=140

build_docker: ## Build the Docker image
	docker build -t ally:$(VERSION) .

run_docker: ## Run Ally in Docker (needs "xhost local:docker")
	docker run -it --rm -e DISPLAY=${DISPLAY} -v /tmp/.X11-unix:/tmp/.X11-unix ally:$(VERSION)

clean: ## Remove caches and build artifacts
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist/ build/

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
