set shell := ["zsh", "-uc"]

default:
    @just --list

devenv: lock
    @echo "Setting up development environment"
    @tox devenv -e devenv .venv
    @echo "Activating virtual environment"
    @source .venv/bin/activate
    @pre-commit install
    @echo "✓ Development environment ready"

# Run all checks
check:
    tox

# Run tests
test:
    @tox -e tests

# Run type checking
typecheck:
    @tox -e typing

# Format code
format:
    @pre-commit run ruff-format --all-files

# Lint code
lint:
    @pre-commit run ruff-check --all-files

clean:
    @find . -type d -name .venv -exec rm -rf {} +
    @find . -type d -name __pycache__ -exec rm -rf {} +
    @find . -type d -name .ruff_cache -exec rm -rf {} +
    @find . -type d -name dist -exec rm -rf {} +
    @find . -type d -name build -exec rm -rf {} +
    @find . -type d -name .pytest_cache -exec rm -rf {} +
    @find . -type d -name "*.egg-info" -exec rm -rf {} +
    @find . -type d -name .mypy_cache -exec rm -rf {} +
    @find . -type d -name .direnv -exec rm -rf {} +
    @find . -type d -name .tox -exec rm -rf {} +
    @find . -type d -name site -exec rm -rf {} +
    @find . -type f -name .coverage -exec rm -rf {} +
    @find . -type d -name result -exec rm -rf {} +
    @find . -type d -name __pycache__ -exec rm -rf {} +

lock:
    @pdm lock -G :all

# Build package
build:
    pyinstaller \
        --onefile \
        --collect-data clair_obscur_save_loader \
        --add-data "icon.ico:." \
        --windowed \
        --icon icon.ico \
        --name ESL.exe \
        clair_obscur_save_loader/app.py

# Update dependencies
update:
    @pdm update

# Release a new version
release version:
    @cz bump
    @just build
