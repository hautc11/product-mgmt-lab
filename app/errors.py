from http import HTTPStatus


class AppError(Exception):
    status_code = 500

    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code or HTTPStatus(self.status_code).name
        super().__init__(str)

class NotFoundError(AppError):
    status_code = 404

class ConflictError(AppError):
    status_code = 409

class ProductNotFoundError(NotFoundError):
    def __init__(self, product_id: int):
        super().__init__(f"Product {product_id} not found", code="PRODUCT_NOT_FOUND")

class ProductNameConflictError(ConflictError):
    def __init__(self, name: str):
        super().__init__(f"Product name '{name}' already exists", code="PRODUCT_NAME_CONFLICT")