"""MongoDB database connection and configuration."""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings

class MongoDB:
    """MongoDB database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB."""
        cls.client = AsyncIOMotorClient(settings.mongodb_url)
        print(f"✅ Connected to MongoDB at {settings.mongodb_url}")
        
        # Test connection
        try:
            await cls.client.admin.command('ping')
            print(f"📊 Using database: {settings.database_name}")
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            print("👋 MongoDB connection closed")
    
    @classmethod
    def get_database(cls):
        """Get database instance."""
        if cls.client is None:
            raise Exception("Database not connected. Call connect_db() first.")
        return cls.client[settings.database_name]
    
    @classmethod
    def get_collection(cls, name: str):
        """Get collection from database."""
        db = cls.get_database()
        return db[name]


# Database instance
mongodb = MongoDB()


# Get collections
def get_users_collection():
    """Get users collection."""
    return mongodb.get_collection("users")


def get_measurements_collection():
    """Get measurements collection."""
    return mongodb.get_collection("measurements")
