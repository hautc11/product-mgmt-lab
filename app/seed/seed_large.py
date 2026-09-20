import time

from faker import Faker

from app.database import SessionLocal
from app.models.product import Product

faker = Faker()

BATCH_SIZE = 5000
TOTAL_PRODUCTS = 50000

def run():
    db = SessionLocal()
    try:
        start = time.perf_counter()
        for batch_start in range(0, TOTAL_PRODUCTS, BATCH_SIZE):
            batch = [
                {
                    "name": f"{faker.word()}_{batch_start + i}",
                    "description": faker.sentence(),
                    "price": round(faker.pyfloat(left_digits=2, right_digits=2, positive=True), 2)
                }
                for i in range(BATCH_SIZE)
            ]
            db.bulk_insert_mappings(Product, batch)
            db.commit()
            print(f"Inserted batch {batch_start + BATCH_SIZE}/{TOTAL_PRODUCTS}")
        elapsed = time.perf_counter() - start
        print(f"Done seeding {TOTAL_PRODUCTS} products in {elapsed:.2f} seconds.")
    finally:
        db.close()

if __name__ == "__main__":
    run()