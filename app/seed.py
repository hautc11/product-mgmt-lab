from faker import Faker

from app.database import SessionLocal
from app.models.product import Product
from app.models.user import User

faker = Faker()

def run():
    db = SessionLocal()

    # Create fake users
    for _ in range(10):
        user = User(
            username=faker.user_name(),
            email=faker.email(),
            full_name=faker.name(),
            hashed_password=faker.password()
        )
        db.add(user)

    # Create fake products
    for _ in range(10):
        product = Product(
            name=faker.word(),
            description=faker.text(),
            price=round(faker.pyfloat(left_digits=2, right_digits=2, positive=True), 2)
        )
        db.add(product)

    db.commit()
    db.close()

if __name__ == "__main__":
    run()