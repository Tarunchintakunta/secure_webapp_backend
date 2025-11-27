from fastapi import HTTPException, Depends
from src.models.user import UserResponse
from src.config.database import get_database
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from bson import ObjectId

async def get_dashboard_stats(current_user: UserResponse, db):
    """Get comprehensive dashboard statistics"""
    stats = {}
    
    # Total products
    total_products = await db["products"].count_documents({})
    stats["total_products"] = total_products
    
    # Total customers (admin only)
    if current_user.role == "admin":
        total_customers = await db["customers"].count_documents({})
        stats["total_customers"] = total_customers
    
    # Total sales count
    if current_user.role == "admin":
        total_sales = await db["sales"].count_documents({"status": "completed"})
    else:
        total_sales = await db["sales"].count_documents({
            "status": "completed",
            "employee_id": current_user.id
        })
    stats["total_sales"] = total_sales
    
    # Total revenue
    pipeline = [
        {"$match": {"status": "completed"}}
    ]
    if current_user.role != "admin":
        pipeline[0]["$match"]["employee_id"] = current_user.id
    
    pipeline.append({
        "$group": {
            "_id": None,
            "total_revenue": {"$sum": "$total_amount"}
        }
    })
    
    result = await db["sales"].aggregate(pipeline).to_list(1)
    stats["total_revenue"] = result[0]["total_revenue"] if result else 0
    
    # Low stock products count
    low_stock_pipeline = [
        {
            "$project": {
                "name": 1,
                "stock_quantity": 1,
                "low_stock_threshold": 1,
                "is_low_stock": {
                    "$lte": ["$stock_quantity", "$low_stock_threshold"]
                }
            }
        },
        {
            "$match": {
                "$expr": {"$lte": ["$stock_quantity", "$low_stock_threshold"]}
            }
        },
        {"$count": "count"}
    ]
    low_stock_result = await db["products"].aggregate(low_stock_pipeline).to_list(1)
    stats["low_stock_count"] = low_stock_result[0]["count"] if low_stock_result else 0
    
    # Today's sales
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_match = {"status": "completed", "created_at": {"$gte": today_start}}
    if current_user.role != "admin":
        today_match["employee_id"] = current_user.id
    
    today_sales = await db["sales"].count_documents(today_match)
    stats["today_sales"] = today_sales
    
    # Today's revenue
    today_revenue_pipeline = [
        {"$match": today_match},
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$total_amount"}
            }
        }
    ]
    today_revenue_result = await db["sales"].aggregate(today_revenue_pipeline).to_list(1)
    stats["today_revenue"] = today_revenue_result[0]["total"] if today_revenue_result else 0
    
    # This week's sales
    week_start = today_start - timedelta(days=today_start.weekday())
    week_match = {"status": "completed", "created_at": {"$gte": week_start}}
    if current_user.role != "admin":
        week_match["employee_id"] = current_user.id
    
    week_sales = await db["sales"].count_documents(week_match)
    stats["week_sales"] = week_sales
    
    # This month's sales
    month_start = today_start.replace(day=1)
    month_match = {"status": "completed", "created_at": {"$gte": month_start}}
    if current_user.role != "admin":
        month_match["employee_id"] = current_user.id
    
    month_sales = await db["sales"].count_documents(month_match)
    stats["month_sales"] = month_sales
    
    return stats

async def get_sales_report(
    start_date: Optional[str],
    end_date: Optional[str],
    current_user: UserResponse,
    db
):
    """Get sales report with date filtering"""
    match_query = {"status": "completed"}
    
    if current_user.role != "admin":
        match_query["employee_id"] = current_user.id
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            match_query["created_at"] = {"$gte": start_dt}
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            if "created_at" in match_query:
                match_query["created_at"]["$lte"] = end_dt
            else:
                match_query["created_at"] = {"$lte": end_dt}
        except:
            pass
    
    pipeline = [
        {"$match": match_query},
        {
            "$group": {
                "_id": None,
                "total_sales": {"$sum": "$total_amount"},
                "count": {"$sum": 1},
                "average_sale": {"$avg": "$total_amount"}
            }
        }
    ]
    
    result = await db["sales"].aggregate(pipeline).to_list(1)
    if not result:
        return {"total_sales": 0, "count": 0, "average_sale": 0}
    
    return result[0]

async def get_product_analytics(db):
    """Get product analytics"""
    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "total_stock": {"$sum": "$stock_quantity"},
                "total_value": {
                    "$sum": {"$multiply": ["$stock_quantity", "$price"]}
                }
            }
        },
        {"$sort": {"count": -1}}
    ]
    
    categories = await db["products"].aggregate(pipeline).to_list(100)
    
    return {
        "categories": [
            {
                "category": cat["_id"],
                "count": cat["count"],
                "total_stock": cat["total_stock"],
                "total_value": cat["total_value"]
            }
            for cat in categories
        ]
    }

async def get_low_stock_products(db):
    """Get products with low stock"""
    pipeline = [
        {
            "$project": {
                "name": 1,
                "category": 1,
                "stock_quantity": 1,
                "low_stock_threshold": 1,
                "price": 1,
                "is_low_stock": {
                    "$lte": ["$stock_quantity", "$low_stock_threshold"]
                }
            }
        },
        {
            "$match": {
                "$expr": {"$lte": ["$stock_quantity", "$low_stock_threshold"]}
            }
        },
        {"$sort": {"stock_quantity": 1}}
    ]
    
    products = await db["products"].aggregate(pipeline).to_list(100)
    
    return [
        {
            "id": str(p["_id"]),
            "name": p["name"],
            "category": p["category"],
            "stock_quantity": p["stock_quantity"],
            "low_stock_threshold": p["low_stock_threshold"],
            "price": p["price"]
        }
        for p in products
    ]

async def get_top_selling_products(limit: int, db):
    """Get top selling products"""
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product_id",
                "total_quantity": {"$sum": "$items.quantity"},
                "total_revenue": {
                    "$sum": {"$multiply": ["$items.quantity", "$items.price_at_sale"]}
                },
                "sale_count": {"$sum": 1}
            }
        },
        {"$sort": {"total_quantity": -1}},
        {"$limit": limit}
    ]
    
    results = await db["sales"].aggregate(pipeline).to_list(limit)
    
    # Get product details
    top_products = []
    for result in results:
        product = await db["products"].find_one({"_id": ObjectId(result["_id"])})
        if product:
            top_products.append({
                "id": str(product["_id"]),
                "name": product["name"],
                "category": product.get("category", ""),
                "total_quantity_sold": result["total_quantity"],
                "total_revenue": result["total_revenue"],
                "sale_count": result["sale_count"]
            })
    
    return top_products

async def get_revenue_by_date_range(
    start_date: Optional[str],
    end_date: Optional[str],
    db
):
    """Get revenue analytics by date range"""
    match_query = {"status": "completed"}
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            match_query["created_at"] = {"$gte": start_dt}
        except:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            if "created_at" in match_query:
                match_query["created_at"]["$lte"] = end_dt
            else:
                match_query["created_at"] = {"$lte": end_dt}
        except:
            pass
    
    # Daily revenue
    daily_pipeline = [
        {"$match": match_query},
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "revenue": {"$sum": "$total_amount"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    daily_revenue = await db["sales"].aggregate(daily_pipeline).to_list(100)
    
    return {
        "daily_revenue": [
            {
                "date": item["_id"],
                "revenue": item["revenue"],
                "count": item["count"]
            }
            for item in daily_revenue
        ]
    }

