# Makefile
SHELL = /bin/bash
# help
.PHONY: help
help:
    @echo "Commands:"
    @echo "venv    : creates a virtual environment."
    @echo "style   : executes style formatting."
    @echo "clean   : cleans all unnecessary files."
    @echo "docs    : builds documentation with mkdocs."
    @echo "docs-serve: serves the documentation locally."
# Styling
.PHONY: style
style:
	black .
	flake8
	python3 -m isort .
	autopep8 --in-place --recursive --aggressive --aggressive --exclude=".venv" .
# Environment
.PHONY: venv
venv:
	uv venv .venv
	uv pip install -U pip setuptools wheel && \
	uv pip install -e ".[dev]"
	uv pip install -U -e ./
	uv pip install -U -r requirements.txt
	uv pip install "black[jupyter]"
	uv pip install "mkdocstrings[python]"
	uv pip install "mkdocs-monorepo-plugin"

# Docs
.PHONY: docs docs-serve
docs:
	mkdocs build
docs-serve:
	mkdocs serve
# Cleaning
.PHONY: clean
clean: style
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
	find . | grep -E ".pytest_cache" | xargs rm -rf
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf
	rm -f .coverage