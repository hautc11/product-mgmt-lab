import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.cache as cache_module
from app.database import Base, get_db
from app.main import app
from app.models.product import Product

TEST_DATABASE_URL = "postgresql+psycopg2://app:app@localhost:5432/app_test_db"

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(cache_module, "redis_client", fake)
    yield fake

@pytest.fixture
def seeded_product():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    db.query(Product).delete()  # Clear existing products
    db.commit()
    product = Product(name="Test Rate Limit Product", description="A product for testing", price=9.99)
    db.add(product)
    db.commit()
    db.refresh(product)
    yield product
    db.close()

@pytest.fixture
def client():
    return TestClient(app)

def test_request_within_limit_succeed(client, seeded_product):
    for i in range(5):
        response = client.post(
            f"/products/{seeded_product.id}/reviews",
            json={"rating": 5, "comment":f"review {i}", "user_id": None},
        )
        assert response.status_code == 201


def test_request_over_limit_is_blocker(client, seeded_product):
    for i in range(5):
            response = client.post(
                f"/products/{seeded_product.id}/reviews",
                json={"rating": 5, "comment":f"review {i}", "user_id": None},
            )
            assert response.status_code == 201

    response = client.post(
        f"/products/{seeded_product.id}/reviews",
        json={"rating": 5, "comment":f"review {i}", "user_id": None},
    )
    assert response.status_code == 429
    body = response.json()
    assert body["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert "Retry-After" in response.headers