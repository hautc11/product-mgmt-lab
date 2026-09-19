from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product, Review
from app.schemas.review import ReviewCreate, ReviewOut

router = APIRouter(
    prefix="/products/{product_id}/reviews",
    tags=["reviews"],
)

@router.post("", response_model=ReviewOut, status_code=201)
def create_review(product_id: int, review: ReviewCreate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_review = Review(
        product_id=product_id, 
        user_id=review.user_id, 
        rating=review.rating, 
        comment=review.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("", response_model=list[ReviewOut])
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.product_id == product_id).all()