from flask import Blueprint, request, jsonify
from app.models import Inventory, ServiceTicket
from app.extensions import db
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema
from app.auth.decorators import mechanic_token_required 

inventory_blueprint = Blueprint("inventory", __name__)

@inventory_blueprint.route("/", methods=["POST"])
def create_inventory():
    data = request.json
    errors = inventory_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    inventory = Inventory(**data)
    db.session.add(inventory)
    db.session.commit()
    return jsonify(inventory_schema.dump(inventory)), 201


@inventory_blueprint.route("/", methods=["GET"])
def get_inventories():
    inventories = Inventory.query.all()
    return jsonify(inventories_schema.dump(inventories)), 200


@inventory_blueprint.route("/<int:id>", methods=["PUT"])
def update_inventory(id):
    inventory = Inventory.query.get_or_404(id)
    data = request.json
    errors = inventory_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    for key, value in data.items():
        setattr(inventory, key, value)
    db.session.commit()
    return jsonify(inventory_schema.dump(inventory)), 200


@inventory_blueprint.route("/<int:id>", methods=["DELETE"])
def delete_inventory(id):
    inventory = Inventory.query.get_or_404(id)
    db.session.delete(inventory)
    db.session.commit()
    return jsonify({"message": "Inventory deleted"}), 200


@inventory_blueprint.route("/<int:inventory_id>/add-part", methods=["POST"])
@mechanic_token_required  # Ensure only mechanics can access this route
def add_part_to_service_ticket(mechanic_id, inventory_id):
    # Fetch the inventory item
    inventory_item = Inventory.query.get_or_404(inventory_id)

    # Get ticket_id from the request payload
    data = request.json
    ticket_id = data.get("ticket_id")
    if not ticket_id:
        return jsonify({"message": "Service Ticket ID is required"}), 400

    # Fetch the service ticket
    service_ticket = ServiceTicket.query.get_or_404(ticket_id)

    # Add the inventory item to the service ticket
    if inventory_item not in service_ticket.inventory_items:
        service_ticket.inventory_items.append(inventory_item)
        db.session.commit()
        return jsonify({"message": "Part added to service ticket"}), 200
    else:
        return jsonify({"message": "Part is already associated with this service ticket"}), 400