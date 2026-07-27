from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# MongoDB connection (local instance)
client = MongoClient("mongodb://localhost:27017")
db = client["ApiTest"]   # your database name
orders_collection = db["crm_orders"]   # your collection name

# Pydantic model for validation
class Order(BaseModel):
    customer_id: int
    product: str

@app.post("/orders")
def create_order(order: Order):
    # Step 1: Save order in MongoDB
    new_order = {
        "customer_id": order.customer_id,
        "product": order.product,
        "status": "Created"
    }
    result = orders_collection.insert_one(new_order)
    order_id = str(result.inserted_id)   # MongoDB generates unique _id

    # Step 2: (Skip Dynamics CRM for now)

    # Step 3: Trigger provisioning/notification microservices
    provision_service(order_id)
    send_notification(order.customer_id, order_id)

    return {"order_id": order_id, "status": "Created"}

# Mock microservices
def provision_service(order_id: str):
    print(f"Provisioning started for order {order_id}")

def send_notification(customer_id: int, order_id: str):
    print(f"Notification sent to customer {customer_id} for order {order_id}")

# Optional: GET endpoint to fetch all orders
@app.get("/orders")
def get_orders():
    orders = list(orders_collection.find())
    for order in orders:
        order["_id"] = str(order["_id"])  # convert ObjectId to string
    return orders
