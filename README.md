# Product Management Lab

A small FastAPI application for managing products and product reviews. The
application uses PostgreSQL for persistence, SQLAlchemy for database access,
and Alembic for schema migrations.

## Project structure

- `app/main.py` - creates the FastAPI application and registers routers.
- `app/models/` - SQLAlchemy models for users, products, and reviews.
- `app/routers/` - product and review API endpoints.
- `app/schemas/` - request and response schemas.
- `alembic/` - database migration configuration and revisions.
- `docs/product-reviews-table-design.md` - review table requirements and ER diagram.

## Requirements

- Python 3.10+
- Docker Desktop with Docker Compose

The default database URL is:

```text
postgres+psycopg2://app:app@localhost:5432/app_db
```

You can override it by setting the `DATABASE_URL` environment variable. A
`.env` file is also supported.

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start PostgreSQL and Redis with Docker Compose:

```powershell
docker compose up -d
```

Apply the database migrations:

```powershell
alembic upgrade head
```

Optional: add sample users and products:

```powershell
python -m app.seed
```

Start the API in development mode:

```powershell
uvicorn app.main:app --reload
```