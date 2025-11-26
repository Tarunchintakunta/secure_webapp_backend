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
from src.routes.customer_routes import router as customer_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan)

# SECURITY NOTE: CORS Configuration
# Insecure: Allow origins "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(sale_router)
app.include_router(customer_router)

@app.get("/")
async def root():
    # SECURITY NOTE: Information Leakage
    # Insecure: Returning stack traces or sensitive server info in production
    return {"message": "Secure Inventory System API"}
