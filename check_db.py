import sys
print(f"Python executable: {sys.executable}")
try:
    import motor.motor_asyncio
    print("Motor imported successfully")
except ImportError as e:
    print(f"Failed to import motor: {e}")

import asyncio
async def check_db():
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

if __name__ == "__main__":
    if 'motor.motor_asyncio' in sys.modules:
        asyncio.run(check_db())
