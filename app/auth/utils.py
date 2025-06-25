from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your_secret_key"  

def encode_token(customer_id):
    payload = {
        "customer_id": customer_id,
        "exp": datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def encode_mechanic_token(mechanic_id):
    payload = {
        "mechanic_id": mechanic_id,
        "role": "mechanic", 
        "exp": datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")