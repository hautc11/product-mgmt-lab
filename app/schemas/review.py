from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="The rating given in the review (1-5)")
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    # Simplification: no auth system so user_id is taken from the request body instead of the an authenticated session.
    # In a real application this would come from Depends(get_current_user) or similar.
    user_id: Optional[int] = Field(None, description="The ID of the user creating the review")

class ReviewOut(ReviewBase):
    id: int
    product_id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True