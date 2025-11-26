from motor.motor_asyncio import AsyncIOMotorClient
from src.config.settings import settings

class Database:
    client: AsyncIOMotorClient = None

    async def connect_to_database(self):
        # SECURITY NOTE: Ensure DB_USER and DB_PASS are strong and not hardcoded
        # Insecure: Using default ports without auth in production
        db_url = f"mongodb://{settings.DB_HOST}:27017"
        if settings.DB_USER and settings.DB_PASS:
             db_url = f"mongodb://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:27017"
        
        # SECURITY NOTE: NoSQL Injection
        # Insecure: Constructing queries with string concatenation from user input
        # Secure: Using Motor/PyMongo which handles parameterization
        self.client = AsyncIOMotorClient(db_url)
        print("Connected to MongoDB")

    async def close_database_connection(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")

db = Database()

async def get_database():
    return db.client[settings.DB_NAME]
