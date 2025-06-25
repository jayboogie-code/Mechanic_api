from flask import Blueprint, request, jsonify
from app.models import Mechanic, ServiceTicket, db
from app.auth.utils import encode_mechanic_token
from app.auth.decorators import mechanic_token_required
from app.extensions import limiter
from app.blueprints.mechanic.schemas import mechanic_schema, mechanics_schema 

mechanic_blueprint = Blueprint("mechanic", __name__)

@mechanic_blueprint.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Apply rate limiting
def mechanic_login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    mechanic = Mechanic.query.filter_by(email=email).first()
    if not mechanic or not mechanic.check_password(password):  
        return jsonify({"message": "Invalid credentials"}), 401

    token = encode_mechanic_token(mechanic.id)
    return jsonify({"token": token}), 200


@mechanic_blueprint.route("/statistics", methods=["GET"])
@mechanic_token_required
def mechanic_statistics(mechanic_id):
    mechanics = db.session.query(
        Mechanic.id, Mechanic.name, db.func.count(ServiceTicket.id).label("ticket_count")
    ).join(Mechanic.service_tickets).group_by(Mechanic.id).order_by(db.desc("ticket_count")).all()

    return jsonify([{
        "id": mechanic.id,
        "name": mechanic.name,
        "ticket_count": mechanic.ticket_count
    } for mechanic in mechanics])


@mechanic_blueprint.route("/", methods=["GET"])
def get_mechanics():
    mechanics = Mechanic.query.all()
    return jsonify(mechanics_schema.dump(mechanics)), 200


@mechanic_blueprint.route("/<int:id>", methods=["PUT"])
def update_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    data = request.json
    errors = mechanic_schema.validate(data)  
    if errors:
        return jsonify({"errors": errors}), 400

    for key, value in data.items():
        setattr(mechanic, key, value)
    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic)), 200


@mechanic_blueprint.route("/<int:id>", methods=["DELETE"])
def delete_mechanic(id):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": "Mechanic deleted successfully"}), 200


@mechanic_blueprint.route("/register", methods=["POST"])
def register_mechanic():
    data = request.json
    errors = mechanic_schema.validate(data)  
    if errors:
        return jsonify({"errors": errors}), 400

    # Check if email already exists
    email = data.get("email")
    existing_mechanic = Mechanic.query.filter_by(email=email).first()
    if existing_mechanic:
        return jsonify({"message": "Email already exists"}), 400

    # Hash the password before storing it
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(data.get("password"))

    # Create a new mechanic
    mechanic = Mechanic(
        name=data.get("name"),
        email=email,
        phone=data.get("phone"),
        salary=data.get("salary"),
        password_hash=hashed_password  # Store the hashed password
    )
    db.session.add(mechanic)
    db.session.commit()

    return jsonify({"message": "Mechanic registered successfully"}), 201