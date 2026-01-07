"""Database initialization script for MongoDB."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings


async def init_database():
    """Initialize MongoDB database with indexes."""
    
    print("🔧 Initializing MongoDB database...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB at {settings.mongodb_url}")
        print(f"📊 Database: {settings.database_name}")
        
        # Create indexes for users collection
        users_collection = db.users
        
        # Unique index on email
        await users_collection.create_index("email", unique=True)
        print("✅ Created unique index on users.email")
        
        # Unique index on username
        await users_collection.create_index("username", unique=True)
        print("✅ Created unique index on users.username")
        
        # Index on created_at for sorting
        await users_collection.create_index("created_at")
        print("✅ Created index on users.created_at")
        
        # Create indexes for measurements collection
        measurements_collection = db.measurements
        
        # Index on user_id for querying user measurements
        await measurements_collection.create_index("user_id")
        print("✅ Created index on measurements.user_id")
        
        # Index on created_at for sorting
        await measurements_collection.create_index("created_at")
        print("✅ Created index on measurements.created_at")
        
        # Compound index for user_id + created_at
        await measurements_collection.create_index([
            ("user_id", 1),
            ("created_at", -1)
        ])
        print("✅ Created compound index on measurements (user_id, created_at)")
        
        print("\n✅ Database initialization completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during database initialization: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(init_database())
