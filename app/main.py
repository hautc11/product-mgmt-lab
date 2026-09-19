from fastapi import FastAPI

from app.routers import products, reviews

app = FastAPI()
app.include_router(products.router)
app.include_router(reviews.router)