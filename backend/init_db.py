import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from app.config import settings
from app.core.security import hash_password

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("smartflow.init_db")

async def init_database():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
    client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=3000)
    
    try:
        await client.admin.command('ping')
        logger.info("MongoDB server responded to ping.")
    except Exception as e:
        logger.warning(f"Could not connect to live MongoDB daemon ({e}).")
        logger.info("SmartFlow will run in resilient In-Memory Store mode with auto-seeded junctions.")
        return

    db = client[settings.DATABASE_NAME]

    # 1. Indexes
    logger.info("Creating collections and indexes...")
    await db.users.create_index("email", unique=True)
    await db.junctions.create_index("junction_code", unique=True)
    await db.junctions.create_index([("location", "2dsphere")])
    await db.traffic_observations.create_index("timestamp", expireAfterSeconds=900)
    await db.virtual_signal_states.create_index("junction_id", unique=True)

    # 2. Seed Default Administrator
    admin = await db.users.find_one({"email": "admin@smartflow.io"})
    if not admin:
        await db.users.insert_one({
            "id": "usr_admin_001",
            "email": "admin@smartflow.io",
            "full_name": "System Administrator",
            "hashed_password": hash_password("adminpass123"),
            "role": "ADMINISTRATOR",
            "location_sharing_enabled": True,
            "is_active": True,
            "created_at": datetime.utcnow()
        })
        logger.info("Admin account seeded: admin@smartflow.io / adminpass123")

    # 3. Seed Default Driver Account
    driver = await db.users.find_one({"email": "driver@smartflow.io"})
    if not driver:
        await db.users.insert_one({
            "id": "usr_driver_001",
            "email": "driver@smartflow.io",
            "full_name": "Alex Mercer (Commuter)",
            "hashed_password": hash_password("smartflow123"),
            "role": "DRIVER",
            "location_sharing_enabled": True,
            "is_active": True,
            "created_at": datetime.utcnow()
        })
        logger.info("Sample driver account seeded: driver@smartflow.io / smartflow123")

    # 4. Seed Junctions
    junctions_data = [
        {
            "id": "junc_nyc_01",
            "junction_code": "NYC_GCT_42",
            "name": "Grand Central & 42nd St Crossing",
            "city": "New York",
            "address": "Park Ave & E 42nd St, New York, NY",
            "latitude": 40.7516,
            "longitude": -73.9767,
            "location": {"type": "Point", "coordinates": [-73.9767, 40.7516]},
            "detection_radius_meters": 500,
            "inner_zone_meters": 150,
            "mid_zone_meters": 300,
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": "junc_sfo_01",
            "junction_code": "SFO_MKT_04",
            "name": "Market St & 4th Central Ring",
            "city": "San Francisco",
            "address": "Market St & 4th St, San Francisco, CA",
            "latitude": 37.7857,
            "longitude": -122.4064,
            "location": {"type": "Point", "coordinates": [-122.4064, 37.7857]},
            "detection_radius_meters": 500,
            "inner_zone_meters": 150,
            "mid_zone_meters": 300,
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": "junc_cmb_01",
            "junction_code": "CMB_GAL_03",
            "name": "Galle Road Colpetty Junction",
            "city": "Colombo",
            "address": "Galle Road & R.A. De Mel Mawatha, Colombo 03",
            "latitude": 6.9015,
            "longitude": 79.8517,
            "location": {"type": "Point", "coordinates": [79.8517, 6.9015]},
            "detection_radius_meters": 500,
            "inner_zone_meters": 150,
            "mid_zone_meters": 300,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ]

    for j in junctions_data:
        existing = await db.junctions.find_one({"junction_code": j["junction_code"]})
        if not existing:
            await db.junctions.insert_one(j)
            logger.info(f"Junction seeded: {j['name']} ({j['junction_code']})")

    logger.info("SmartFlow database initialization complete!")
    client.close()

if __name__ == "__main__":
    asyncio.run(init_database())

