from pydantic import BaseModel

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float

class ProductSearch(BaseModel):
    keyword: str
    category: str
    limit: int=10