from fastapi import HTTPException, Depends
from src.models.sale import SaleCreate, SaleInDB, SaleResponse
from src.config.database import get_database
from bson import ObjectId
from datetime import datetime

async def create_sale(sale: SaleCreate, employee_id: str, db=Depends(get_database)):
    total_amount = 0
    for item in sale.items:
        if not ObjectId.is_valid(item.product_id):
            raise HTTPException(status_code=400, detail=f"Invalid product ID: {item.product_id}")
        
        product = await db["products"].find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product not found: {item.product_id}")
        
        if product["stock_quantity"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for: {product['name']}")
        
        # Calculate total
        total_amount += item.price_at_sale * item.quantity

        # Update stock
        await db["products"].update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock_quantity": -item.quantity}}
        )

    sale_doc = {
        "items": [item.model_dump() for item in sale.items],
        "total_amount": total_amount,
        "employee_id": employee_id,
        "customer_name": sale.customer_name,
        "created_at": datetime.utcnow(),
        "status": "completed"
    }
    
    new_sale = await db["sales"].insert_one(sale_doc)
    created_sale = await db["sales"].find_one({"_id": new_sale.inserted_id})
    created_sale["id"] = str(created_sale["_id"])
    return SaleResponse(**created_sale)

async def get_sales(db=Depends(get_database)):
    sales = await db["sales"].find().sort("created_at", -1).to_list(1000)
    for s in sales:
        s["id"] = str(s["_id"])
    return [SaleResponse(**s) for s in sales]

async def get_my_sales(employee_id: str, db=Depends(get_database)):
    sales = await db["sales"].find({"employee_id": employee_id}).sort("created_at", -1).to_list(1000)
    for s in sales:
        s["id"] = str(s["_id"])
    return [SaleResponse(**s) for s in sales]

async def cancel_sale(id: str, employee_id: str, role: str, db=Depends(get_database)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    sale = await db["sales"].find_one({"_id": ObjectId(id)})
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    if sale["status"] == "cancelled":
        raise HTTPException(status_code=400, detail="Sale already cancelled")

    # Only admin or the employee who made the sale can cancel
    # SECURITY NOTE: IDOR (Insecure Direct Object Reference)
    # Insecure: Allowing any user to cancel any sale by ID
    if role != "admin" and sale["employee_id"] != employee_id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this sale")

    # Restore stock
    for item in sale["items"]:
        await db["products"].update_one(
            {"_id": ObjectId(item["product_id"])},
            {"$inc": {"stock_quantity": item["quantity"]}}
        )
    
    await db["sales"].update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "cancelled"}}
    )
    
    return {"message": "Sale cancelled and stock restored"}
