import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.cache as cache_module
from app.cache import cache_get, get_cached_key
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
def seed_products():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    db.query(Product).delete()  # Clear existing products
    db.commit()
    product = Product(name="Test Product", description="A product for testing", price=9.99)
    db.add(product)
    db.commit()
    db.refresh(product)
    yield product
    db.close()

@pytest.fixture
def client():
    return TestClient(app)

def test_cache_miss_then_hit(client, seed_products, monkeypatch):
    original_get = Session.get
    call_count = {"count": 0}

    def get_spy(self, *args, **kwargs):
        call_count["count"] += 1
        return original_get(self, *args, **kwargs)

    monkeypatch.setattr(Session, "get", get_spy)

    response1 = client.get(f"/products/{seed_products.id}")
    assert response1.status_code == 200
    assert call_count["count"] == 1  # Database should be hit (because cache miss)

    assert cache_get(get_cached_key(seed_products.id)) is not None  # Cache should now have the product

    response2 = client.get(f"/products/{seed_products.id}")
    assert response2.status_code == 200
    assert call_count["count"] == 1  # Database should NOT be hit again (because cache hit)
    assert response2.json() == response1.json()  # Responses should be the same


def test_invalidation_on_new_review(client, seed_products):
    response1 = client.get(f"/products/{seed_products.id}")
    assert response1.json()["review_count"] == 0  # Initially, no reviews

    review_response = client.post(f"/products/{seed_products.id}/reviews", json={"rating": 5, "comment": "Great product!", "user_id": None})
    assert review_response.status_code == 201

    response2 = client.get(f"/products/{seed_products.id}")
    assert response2.json()["review_count"] == 1  # After adding a review, count should be updated
    assert response2.json()["average_rating"] == 5.0  # Average rating should reflect the new review
