from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGO_URI")
if not uri:
    print("ERROR: MONGO_URI not found in .env")
    exit(1)

try:
    client = MongoClient(uri)
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
    
    db = client.get_database("hvac_ops")
    print("Available databases:", client.list_database_names())
    
except Exception as e:
    print("❌ Connection failed:", e)