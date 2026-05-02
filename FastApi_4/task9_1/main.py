from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_db
from .models import Product
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Задание 9.1 - Миграции БД")


class ProductCreate(BaseModel):
    title: str
    price: float
    count: int


class ProductOut(BaseModel):
    id: int
    title: str
    price: float
    count: int


class ProductWithDescriptionOut(ProductOut):
    description: str


@app.post("/products", response_model=ProductOut, status_code=201)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    new_product = Product(
        title=product.title,
        price=product.price,
        count=product.count
    )
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


@app.get("/products", response_model=List[ProductOut])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products


@app.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(product)
    await db.commit()
    return None