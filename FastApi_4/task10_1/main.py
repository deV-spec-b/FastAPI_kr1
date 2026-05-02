from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .models import ErrorResponse
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Задание 10.1 - Пользовательская обработка ошибок")


class ResourceNotFoundError(Exception):
    def __init__(self, resource_id: str, resource_type: str = "Resource"):
        self.resource_id = resource_id
        self.resource_type = resource_type
        super().__init__(f"{resource_type} with id '{resource_id}' not found")


class ValidationFailedError(Exception):
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Validation failed for field '{field}': {reason}")


class BusinessRuleViolationError(Exception):
    def __init__(self, rule: str, details: str):
        self.rule = rule
        self.details = details
        super().__init__(f"Business rule violation: {rule} - {details}")


@app.exception_handler(ResourceNotFoundError)
async def handle_resource_not_found(request: Request, exc: ResourceNotFoundError):
    logger.error(f"ResourceNotFoundError: {exc}")
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            "error_type": "ResourceNotFound",
            "resource_id": exc.resource_id,
            "resource_type": exc.resource_type,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(ValidationFailedError)
async def handle_validation_error(request: Request, exc: ValidationFailedError):
    logger.error(f"ValidationFailedError: {exc}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "error_type": "ValidationFailed",
            "field": exc.field,
            "value": exc.value,
            "reason": exc.reason,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(BusinessRuleViolationError)
async def handle_business_rule_violation(request: Request, exc: BusinessRuleViolationError):
    logger.error(f"BusinessRuleViolationError: {exc}")
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc),
            "error_type": "BusinessRuleViolation",
            "rule": exc.rule,
            "details": exc.details,
            "path": request.url.path,
            "timestamp": datetime.now().isoformat()
        }
    )


products_db = {
    "1": {"name": "Product A", "price": 100, "status": "active"},
    "2": {"name": "Product B", "price": 200, "status": "inactive"},
    "3": {"name": "Product C", "price": 300, "status": "active"},
}


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    if product_id not in products_db:
        raise ResourceNotFoundError(product_id, "Product")
    return {"id": product_id, "data": products_db[product_id]}


@app.get("/products/{product_id}/activate")
async def activate_product(product_id: str):
    if product_id not in products_db:
        raise ResourceNotFoundError(product_id, "Product")

    if products_db[product_id]["status"] == "active":
        raise BusinessRuleViolationError(
            "AlreadyActive",
            f"Product '{product_id}' is already active"
        )

    products_db[product_id]["status"] = "active"
    return {"message": f"Product {product_id} activated"}


@app.post("/validate/age")
async def validate_age(age: int):
    if age < 0:
        raise ValidationFailedError("age", age, "Age cannot be negative")
    if age > 150:
        raise ValidationFailedError("age", age, "Age cannot exceed 150")
    if age < 18:
        raise ValidationFailedError("age", age, "User must be 18 or older")

    return {"message": "Valid age", "age": age}


@app.get("/")
async def root():
    return {
        "task": "10.1",
        "title": "Пользовательская обработка ошибок",
        "exceptions": [
            "ResourceNotFoundError (404)",
            "ValidationFailedError (400)",
            "BusinessRuleViolationError (403)"
        ],
        "test_endpoints": [
            "GET /products/999 -> ResourceNotFoundError",
            "GET /products/2/activate -> BusinessRuleViolationError (product inactive)",
            "GET /products/1/activate -> BusinessRuleViolationError (already active)",
            "POST /validate/age?age=15 -> ValidationFailedError"
        ]
    }