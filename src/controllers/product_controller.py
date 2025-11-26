from fastapi import HTTPException, Depends
from src.models.product import ProductCreate, ProductUpdate, ProductInDB, ProductResponse
from src.config.database import get_database
from bson import ObjectId

async def create_product(product: ProductCreate, db=Depends(get_database)):
    product_dict = product.model_dump()
    new_product = await db["products"].insert_one(product_dict)
    created_product = await db["products"].find_one({"_id": new_product.inserted_id})
    return ProductResponse(
        id=str(created_product["_id"]),
        name=created_product["name"],
        description=created_product.get("description"),
        price=created_product["price"],
        category=created_product["category"],
        stock_quantity=created_product["stock_quantity"],
        low_stock_threshold=created_product["low_stock_threshold"]
    )

async def get_products(db=Depends(get_database)):
    products = await db["products"].find().to_list(1000)
    return [ProductResponse(
        id=str(p["_id"]),
        name=p["name"],
        description=p.get("description"),
        price=p["price"],
        category=p["category"],
        stock_quantity=p["stock_quantity"],
        low_stock_threshold=p["low_stock_threshold"]
    ) for p in products]

async def get_product(id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    product = await db["products"].find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(
        id=str(product["_id"]),
        name=product["name"],
        description=product.get("description"),
        price=product["price"],
        category=product["category"],
        stock_quantity=product["stock_quantity"],
        low_stock_threshold=product["low_stock_threshold"]
    )

async def update_product(id: str, product: ProductUpdate, db=Depends(get_database)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    update_data = {k: v for k, v in product.model_dump().items() if v is not None}
    
    if len(update_data) >= 1:
        update_result = await db["products"].update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if update_result.modified_count == 0:
             # Check if product exists
            if not await db["products"].find_one({"_id": ObjectId(id)}):
                raise HTTPException(status_code=404, detail="Product not found")
    
    existing_product = await db["products"].find_one({"_id": ObjectId(id)})
    return ProductResponse(
        id=str(existing_product["_id"]),
        name=existing_product["name"],
        description=existing_product.get("description"),
        price=existing_product["price"],
        category=existing_product["category"],
        stock_quantity=existing_product["stock_quantity"],
        low_stock_threshold=existing_product["low_stock_threshold"]
    )

async def delete_product(id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    delete_result = await db["products"].delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}
