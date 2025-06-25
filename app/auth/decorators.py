from functools import wraps
from flask import request, jsonify
from jose import jwt
from app.extensions import db
from app.models import Customer

SECRET_KEY = "your_secret_key"  

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"message": "Token is missing or invalid"}), 401

        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            customer_id = data.get("customer_id")
            if not customer_id:
                return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"message": f"Token validation failed: {str(e)}"}), 401

        return f(customer_id, *args, **kwargs)
    return decorated

def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return jsonify({"message": "Token is missing or invalid"}), 401

        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            mechanic_id = data.get("mechanic_id")
            role = data.get("role")
            if not mechanic_id or role != "mechanic":
                return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"message": f"Token validation failed: {str(e)}"}), 401

        return f(mechanic_id, *args, **kwargs)
    return decorated