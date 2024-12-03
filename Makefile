.PHONY: install test lint clean docs

install:
	pip install -e ".[dev]"

test:
	pytest --cov=shortcuts_doc_generator tests/

lint:
	black .
	isort .
	flake8 .
	mypy shortcuts_doc_generator/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	sphinx-build -b html docs/source docs/build/html 