from fastapi import HTTPException, Depends
from src.models.product import ProductCreate, ProductUpdate, ProductInDB, ProductResponse
from src.config.database import get_database
from bson import ObjectId

async def create_product(product: ProductCreate, db=Depends(get_database)):
    product_in_db = ProductInDB(**product.dict())
    new_product = await db["products"].insert_one(product_in_db.dict(by_alias=True))
    created_product = await db["products"].find_one({"_id": new_product.inserted_id})
    return ProductResponse(**created_product)

async def get_products(db=Depends(get_database)):
    products = await db["products"].find().to_list(1000)
    return [ProductResponse(**p) for p in products]

async def get_product(id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    product = await db["products"].find_one({"_id": ObjectId(id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(**product)

async def update_product(id: str, product: ProductUpdate, db=Depends(get_database)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    update_data = {k: v for k, v in product.dict().items() if v is not None}
    
    if len(update_data) >= 1:
        update_result = await db["products"].update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if update_result.modified_count == 0:
             # Check if product exists
            if not await db["products"].find_one({"_id": ObjectId(id)}):
                raise HTTPException(status_code=404, detail="Product not found")
    
    existing_product = await db["products"].find_one({"_id": ObjectId(id)})
    return ProductResponse(**existing_product)

async def delete_product(id: str, db=Depends(get_database)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    delete_result = await db["products"].delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}
