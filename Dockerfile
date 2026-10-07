# First install the dependencies
FROM python:3.14-slim AS installer

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock /app/

# Disable development dependencies
ENV UV_NO_DEV=1

# Install the dependencies, but not the project itself yet, since it changes frequently
RUN uv sync --locked --no-install-project

# Copy the project files
COPY . /app

# Install the project itself
RUN uv sync --locked


# Now we can run the application
FROM python:3.14-slim

WORKDIR /app

COPY --from=installer /app /app

# Set the PATH, so we can execute commands like "uvicorn"
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Create an ordinary user named "app", so we do not run as "root", which has all rights
RUN useradd --create-home app

# Switch to the "app" user, so from now on everything runs as "app"
USER app

CMD ["uvicorn", "blasto.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
