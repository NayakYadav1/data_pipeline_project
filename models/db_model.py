from pymongo import MongoClient
from datetime import datetime

client = MongoClient("url-link")
db = client["data_pipeline"]

def insert_cleaned_data(collection, df, file_type, status="success"):
    records = df.to_dict(orient="records")
    # Add meta fields to each record if you want
    meta = {
        "file_type": file_type,
        "upload_time": datetime.utcnow(),
        "status": status,
    }
    for rec in records:
        rec.update(meta)
    db[collection].insert_many(records)

def fetch_data(collection, limit=100):
    return list(db[collection].find().limit(limit))
