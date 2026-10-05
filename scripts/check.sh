# Format and test the code
# Run chmod +x scripts/check.sh when first using to make it executable
set -e
uv run ruff check --fix .
uv run ruff format .
uv run mypy src tests
uv run pytest
