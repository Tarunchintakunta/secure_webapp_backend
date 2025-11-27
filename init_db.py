#!/usr/bin/env python3
"""
MongoDB Initialization Script
Automatically sets up database, collections, and indexes
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from src.config.settings import settings
from src.utils.auth import get_password_hash

async def init_database():
    """Initialize MongoDB database with collections and default data"""
    
    # Connect to MongoDB
    db_url = f"mongodb://{settings.DB_HOST}:27017"
    if settings.DB_USER and settings.DB_PASS:
        db_url = f"mongodb://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:27017"
    
    client = AsyncIOMotorClient(db_url)
    db = client[settings.DB_NAME]
    
    print(f"Connected to MongoDB at {settings.DB_HOST}")
    print(f"Database: {settings.DB_NAME}")
    
    # Create collections if they don't exist
    existing_collections = await db.list_collection_names()
    
    collections = ["users", "products", "customers", "sales"]
    for collection in collections:
        if collection not in existing_collections:
            await db.create_collection(collection)
            print(f"[OK] Created collection: {collection}")
        else:
            print(f"[INFO] Collection already exists: {collection}")
    
    # Create indexes
    print("\nCreating indexes...")
    
    # Users collection indexes
    await db.users.create_index("email", unique=True)
    print("  [OK] Users: unique index on 'email'")
    
    # Products collection indexes
    await db.products.create_index("name")
    await db.products.create_index("category")
    print("  [OK] Products: index on 'name' and 'category'")
    
    # Sales collection indexes
    await db.sales.create_index("created_at")
    await db.sales.create_index("employee_id")
    print("  [OK] Sales: index on 'created_at' and 'employee_id'")
    
    # Customers collection indexes
    await db.customers.create_index("email")
    print("  [OK] Customers: index on 'email'")
    
    # Check if admin user exists
    admin_exists = await db.users.find_one({"role": "admin"})
    
    if not admin_exists:
        print("\nCreating default admin user...")
        admin_user = {
            "name": "Admin User",
            "email": "admin@example.com",
            "role": "admin",
            "hashed_password": get_password_hash("Admin123!")
        }
        await db.users.insert_one(admin_user)
        print("  [OK] Admin user created")
        print("     Email: admin@example.com")
        print("     Password: Admin123!")
    else:
        print("\n[INFO] Admin user already exists")
    
    # Check if employee user exists
    employee_exists = await db.users.find_one({"role": "employee"})
    
    if not employee_exists:
        print("\nCreating default employee user...")
        employee_user = {
            "name": "Employee User",
            "email": "employee@example.com",
            "role": "employee",
            "hashed_password": get_password_hash("Employee123!")
        }
        await db.users.insert_one(employee_user)
        print("  [OK] Employee user created")
        print("     Email: employee@example.com")
        print("     Password: Employee123!")
    else:
        print("\n[INFO] Employee user already exists")
    
    # Add sample products if none exist
    product_count = await db.products.count_documents({})
    if product_count == 0:
        print("\nCreating sample products...")
        sample_products = [
            {
                "name": "Laptop",
                "description": "High-performance laptop",
                "price": 999.99,
                "category": "Electronics",
                "stock_quantity": 10,
                "low_stock_threshold": 3
            },
            {
                "name": "Mouse",
                "description": "Wireless mouse",
                "price": 29.99,
                "category": "Electronics",
                "stock_quantity": 50,
                "low_stock_threshold": 10
            },
            {
                "name": "Keyboard",
                "description": "Mechanical keyboard",
                "price": 79.99,
                "category": "Electronics",
                "stock_quantity": 25,
                "low_stock_threshold": 5
            }
        ]
        await db.products.insert_many(sample_products)
        print(f"  [OK] Created {len(sample_products)} sample products")
    else:
        print(f"\n[INFO] Products collection already has {product_count} products")
    
    client.close()
    print("\nDatabase initialization complete!\n")

if __name__ == "__main__":
    asyncio.run(init_database())

