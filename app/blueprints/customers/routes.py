from flask import Blueprint, request, jsonify
from app.models import Customer, ServiceTicket, db  
from app.auth.utils import encode_token  
from app.auth.decorators import token_required  
from app.blueprints.customers.schemas import login_schema, customers_schema, customer_schema  
from app.blueprints.service_ticket.schemas import service_ticket_schema, service_tickets_schema  
from app.extensions import limiter, cache 
from werkzeug.security import generate_password_hash

customer_blueprint = Blueprint("customer", __name__)

@customer_blueprint.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Apply rate limiting
def login():
    data = request.json
    errors = login_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    email = data.get("email")
    password = data.get("password")

    customer = Customer.query.filter_by(email=email).first()
    if not customer or not customer.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token}), 200


@customer_blueprint.route("/my-tickets", methods=["GET"])
@token_required
@cache.cached(timeout=60)  # Apply caching
def my_tickets(customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return jsonify(service_tickets_schema.dump(tickets))  


@customer_blueprint.route("/", methods=["GET"])
def get_customers():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    customers = Customer.query.paginate(page=page, per_page=per_page)
    return jsonify({
        "customers": customers_schema.dump(customers.items),
        "total": customers.total,
        "pages": customers.pages
    }), 200


@customer_blueprint.route("/register", methods=["POST"])
def register():
    data = request.json
    errors = customer_schema.validate(data)  
    if errors:
        return jsonify({"errors": errors}), 400

    # Check if email already exists
    email = data.get("email")
    existing_customer = Customer.query.filter_by(email=email).first()
    if existing_customer:
        return jsonify({"message": "Email already exists"}), 400

    # Hash the password before storing it
    hashed_password = generate_password_hash(data.get("password"))

    # Create a new customer
    customer = Customer(
        name=data.get("name"),
        email=email,
        password_hash=hashed_password,
        phone=data.get("phone")
    )
    db.session.add(customer)
    db.session.commit()

    return jsonify({"message": "Customer registered successfully"}), 201


@customer_blueprint.route("/create-ticket", methods=["POST"])
@token_required  # Ensure the customer is authenticated
def create_service_ticket(customer_id):
    data = request.json
    VIN = data.get("VIN")
    description = data.get("description")

    # Validate required fields
    if not VIN or not description:
        return jsonify({"message": "VIN and description are required"}), 400

    # Create a new service ticket
    service_ticket = ServiceTicket(
        VIN=VIN,
        description=description,
        customer_id=customer_id
    )
    db.session.add(service_ticket)
    db.session.commit()

    return jsonify({"message": "Service ticket created successfully"}), 201