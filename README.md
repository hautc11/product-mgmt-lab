# Product Management Lab

An application for managing products and product reviews. The
application uses PostgreSQL for persistence, SQLAlchemy for database access,
Redis for product response caching, and Alembic for schema migrations.

## Project structure

- `app/main.py` - creates the FastAPI application and registers routers.
- `app/models/` - SQLAlchemy models for users, products, and reviews.
- `app/routers/` - product and review API endpoints.
- `app/schemas/` - request and response schemas.
- `alembic/` - database migration configuration and revisions.
- `Dockerfile` - image definition for the FastAPI application.
- `compose.yaml` - app, PostgreSQL, and Redis services.
- `docs/product-reviews-table-design.md` - review table requirements and ER diagram.
- `pyproject.toml` and `uv.lock` - project metadata and locked dependencies.

## Requirements

- Docker Desktop with Docker Compose
- Python 3.14+
- `uv` (for local dependency management and commands outside Docker)

## Local development

Install the locked dependencies, including the development dependency group:

```powershell
uv sync --locked
```

Run the application locally:

```powershell
uv run uvicorn app.main:app --reload
```

Run the test suite:

```powershell
uv run python -m pytest
```

The committed `uv.lock` file keeps dependency versions reproducible. Update
dependencies with `uv add` or `uv remove`, then review the resulting lockfile.

## Docker setup

The Docker Compose stack contains three services:

- `app` - the FastAPI application, built from the `Dockerfile`
- `postgres` - PostgreSQL 16 with persistent storage in the `pgdata` volume
- `redis` - Redis 7 for product response caching

Build and start the complete stack:

```powershell
docker compose up -d --build
```

Apply the database migrations inside the application container:

```powershell
docker compose exec app uv run alembic upgrade head
```

Optional: add sample users and products from inside the application container:

```powershell
docker compose exec app uv run python -m app.seed
```

The API is available at <http://localhost:8000>. Interactive API
documentation is available at <http://localhost:8000/docs>.

View application logs:

```powershell
docker compose logs -f app
```

Stop the services while keeping the database volume:

```powershell
docker compose down
```

To remove the database volume and all stored PostgreSQL data as well, run:

```powershell
docker compose down -v
```

The app service mounts the local `app/` directory into the container, so
changes to application code are picked up by Uvicorn's reload mode.

Inside the Compose network, the application uses these connection URLs:

```text
DATABASE_URL=postgresql+psycopg2://app:app@postgres:5432/app_db
REDIS_URL=redis://redis:6379/0
```

## Development notes

When models or database requirements change, create and review an Alembic
migration before starting the application against a fresh database. Keep the
database schema and the design documented in
`docs/product-reviews-table-design.md` in sync.
