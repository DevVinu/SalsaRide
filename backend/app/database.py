import logging
from typing import Optional, Dict, Any, List
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger("smartflow.database")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    is_connected: bool = False
    
    # In-memory storage fallback for resilient offline/demo operations
    in_memory_store: Dict[str, List[Dict[str, Any]]] = {
        "users": [],
        "junctions": [],
        "traffic_sessions": [],
        "traffic_observations": [],
        "virtual_signal_states": [],
        "signal_history": [],
        "administrators": [],
        "notifications": []
    }

db_manager = Database()

async def connect_to_mongo():
    if not settings.ENABLE_MONGO:
        logger.info("MongoDB disabled by configuration (ENABLE_MONGO=False). Operating in fast In-Memory Store mode.")
        db_manager.is_connected = False
        return

    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=800,
            connectTimeoutMS=800,
            socketTimeoutMS=800,
        )
        # Verify connection with fast 1.0s timeout
        await asyncio.wait_for(client.admin.command('ping'), timeout=1.0)
        db_manager.client = client
        db_manager.db = client[settings.DATABASE_NAME]
        db_manager.is_connected = True
        logger.info(f"Connected to MongoDB database: {settings.DATABASE_NAME}")

        # Ensure geospatial index on junctions
        await db_manager.db.junctions.create_index([("location", "2dsphere")])
        # Ensure TTL index on traffic observations (expires after 15 minutes)
        await db_manager.db.traffic_observations.create_index("timestamp", expireAfterSeconds=900)
        # Ensure unique code index
        await db_manager.db.junctions.create_index("junction_code", unique=True)
        await db_manager.db.users.create_index("email", unique=True)
        logger.info("MongoDB geospatial and unique indexes verified.")
    except Exception as e:
        logger.warning(f"MongoDB not available ({e}). Operating in resilient In-Memory Store mode.")
        db_manager.is_connected = False

async def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    return db_manager.db

