import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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

client = TestClient(app)


@pytest.fixture
def two_products():
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    db.query(Product).delete()
    db.commit()

    product_a = Product(name="Product A", price=10.0, description="First product")
    product_b = Product(name="Product B", price=20.0, description="Second product")
    db.add_all([product_a, product_b])
    db.commit()
    db.refresh(product_a)
    db.refresh(product_b)
    yield product_a, product_b
    db.close()


def test_not_found_returns_standardized_error():
    response = client.get("/products/999999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"


def test_validation_error_returns_standardized_error(two_products):
    product_a, _ = two_products
    response = client.post(f"/products/{product_a.id}/reviews", json={"rating": 10, "comment": "test"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "UNPROCESSABLE_ENTITY"
    assert "details" in body["error"]


def test_success_response_is_not_wrapped(two_products):
    product_a, _ = two_products
    response = client.get(f"/products/{product_a.id}")
    assert response.status_code == 200
    body = response.json()
    assert "error" not in body
    assert "id" in body


def test_conflict_error_on_duplicate_name(two_products):
    product_a, product_b = two_products
    response = client.put(f"/products/{product_b.id}", json={"name": product_a.name})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PRODUCT_NAME_CONFLICT"
