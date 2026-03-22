from fastapi import FastAPI,  HTTPException, Query
from task3_2.models import Product
from typing import List, Optional

app = FastAPI()

products_db = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99},
]

@app.get("/product/{product_id}", response_model=dict)
async def get_product(product_id: int):
    for product in products_db:
        if product["product_id"] == product_id:
            return product
        
    raise HTTPException(status_code=404, detail="Товар не найден")

@app.get("/product/search", response_model=List[dict])
async def search_products(
    keyword: str = Query(..., description="Ключевое слово для поиска"),
    category: Optional[str] = Query(None, description="Категория для фильтрации"),
    limit: int = Query(10, description="Максимальное кол-во результатов", ge=1, le=100)
):
    results = []
    keyword_lower = keyword_lower()
    
    for product in products_db:
        if keyword_lower in product["name"].lower():
            if category and product["category"].lower() != category.lower():
                continue
            results.append(product)

    return results[:limit]

@app.get("/")
async def root():
    return {
        "GET /product/{id}": "получить товар по ID",
        "GET /products/search": "поиск товаров"
    }