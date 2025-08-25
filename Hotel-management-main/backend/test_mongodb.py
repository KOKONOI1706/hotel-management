#!/usr/bin/env python3
"""
Test script to verify MongoDB Atlas connection and API functionality
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    try:
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME', 'hotel_management')
        
        print(f"Testing connection to: {mongo_url}")
        print(f"Database: {db_name}")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Test collections
        collections = await db.list_collection_names()
        print(f"📁 Collections found: {collections}")
        
        # Test inserting and reading data
        test_doc = {"test": True, "timestamp": "2025-08-25"}
        await db.test_collection.insert_one(test_doc)
        
        found_doc = await db.test_collection.find_one({"test": True})
        if found_doc:
            print("✅ Database read/write test successful!")
            # Clean up
            await db.test_collection.delete_one({"test": True})
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

async def main():
    print("🧪 Testing MongoDB Atlas Connection...")
    success = await test_mongodb_connection()
    
    if success:
        print("\n🎉 All tests passed! Ready to deploy to Vercel.")
    else:
        print("\n❌ Tests failed! Please check your MongoDB Atlas configuration.")

if __name__ == "__main__":
    asyncio.run(main())
