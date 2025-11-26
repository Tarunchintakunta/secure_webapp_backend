from fastapi import FastAPI
from src.config.database import db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect_to_database()
    yield
    await db.close_database_connection()

from src.routes.auth_routes import router as auth_router
from src.routes.product_routes import router as product_router
from src.routes.sale_routes import router as sale_router

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(sale_router)

@app.get("/")
async def root():
    return {"message": "Secure Inventory System API"}
