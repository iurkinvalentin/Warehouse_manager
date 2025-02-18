from fastapi import FastAPI
from app.routers import product, warehouse, category, attribute, auth

app = FastAPI(
    title='warehouse_manager',
    description='система управления складами',
    version='0.1'
)

app.include_router(auth.router)
app.include_router(product.router)
app.include_router(attribute.router)
app.include_router(category.router)
app.include_router(warehouse.router)
