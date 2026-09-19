from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.cache import cache_delete, cache_get, cache_set, get_cached_key
from app.database import get_db
from app.models.product import Product
from app.models.review import Review
from app.schemas.product import ProductUpdate

CACHE_TTL_SECONDS = 60

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    key = get_cached_key(product_id)

    cached = cache_get(key)
    if cached is not None:
        return cached

    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    avg_rating, review_count = (
        db.query(
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .filter(Review.product_id == product_id)
        .one()
    )

    response = {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "description": product.description,
        "average_rating": float(avg_rating) if avg_rating is not None else None,
        "review_count": review_count,
    }

    cache_set(key, response, ttl_seconds=CACHE_TTL_SECONDS)
    return response

@router.put("/{product_id}")
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)

    # Invalidate cache for the updated product
    cache_delete(get_cached_key(product_id))

    return {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "description": product.description,
    }