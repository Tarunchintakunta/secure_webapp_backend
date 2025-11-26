from fastapi import HTTPException, Depends
from src.models.customer import CustomerCreate, CustomerUpdate, CustomerInDB, CustomerResponse
from src.config.database import get_database
from bson import ObjectId

async def create_customer(customer: CustomerCreate, db=Depends(get_database)):
    customer_dict = customer.model_dump()
    new_customer = await db["customers"].insert_one(customer_dict)
    created_customer = await db["customers"].find_one({"_id": new_customer.inserted_id})
    created_customer["id"] = str(created_customer["_id"])
    return CustomerResponse(**created_customer)

async def get_customers(db=Depends(get_database)):
    customers = await db["customers"].find().to_list(1000)
    for c in customers:
        c["id"] = str(c["_id"])
    return [CustomerResponse(**c) for c in customers]

async def get_sales_analytics(db=Depends(get_database)):
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": None,
            "total_sales": {"$sum": "$total_amount"},
            "count": {"$sum": 1}
        }}
    ]
    result = await db["sales"].aggregate(pipeline).to_list(1)
    if not result:
        return {"total_sales": 0, "count": 0}
    return {"total_sales": result[0]["total_sales"], "count": result[0]["count"]}
