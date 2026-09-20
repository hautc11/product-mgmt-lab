from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import AppError
from app.routers import products, reviews

app = FastAPI()
app.include_router(products.router)
app.include_router(reviews.router)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exec: AppError):
    return JSONResponse(
        status_code=exec.status_code,
        content={
            "error": {
                "code": exec.code, 
                "message": exec.message
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": HTTPStatus(exc.status_code).name, 
                    "message": str(exc.detail)
                }
            },
        )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": HTTPStatus.UNPROCESSABLE_ENTITY.name,
                "message": "Invalid request data",
                "details": exc.errors(),
            }
        },
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
    status_code=500,
    content={
        "error": {
            "code": HTTPStatus.INTERNAL_SERVER_ERROR.name, 
            "message": "An unexpected error occurred"
            }
        },
    )