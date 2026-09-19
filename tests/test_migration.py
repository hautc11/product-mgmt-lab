import os
import string
import subprocess

import pytest
from sqlalchemy import create_engine, inspect

TEST_DATABASE_URL = "postgresql+psycopg2://app:app@localhost:5432/app_test_db"

@pytest.fixture(autouse=True)
def use_test_database(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)

def run_alembic(*args):
    result = subprocess.run(["alembic", *args], capture_output=True, text=True,)
    assert result.returncode == 0, result.stderr
    return result.stdout

def table_exists(table_name: string) -> bool:
    engine = create_engine(TEST_DATABASE_URL)
    return inspect(engine).has_table(table_name)

def test_migration_round_trip():
    run_alembic("upgrade", "head")
    assert table_exists("reviews") is True

    run_alembic("downgrade", "-1")
    assert table_exists("reviews") is False

    run_alembic("upgrade", "head")
    assert table_exists("reviews") is True