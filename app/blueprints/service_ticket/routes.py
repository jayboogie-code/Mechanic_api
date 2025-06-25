from flask import Blueprint, request, jsonify
from app.models import ServiceTicket, Mechanic, Inventory, db
from app.auth.decorators import token_required
from app.extensions import limiter

service_ticket_blueprint = Blueprint("service_ticket", __name__)

@service_ticket_blueprint.route("/", methods=["POST"])
@token_required
def create_service_ticket(customer_id):
    data = request.json
    service_ticket = ServiceTicket(
        VIN=data.get("VIN"),
        description=data.get("description"),
        customer_id=customer_id
    )
    db.session.add(service_ticket)
    db.session.commit()
    return jsonify({"message": "Service ticket created successfully"}), 201


@service_ticket_blueprint.route("/<int:ticket_id>", methods=["GET"])
@token_required
def get_service_ticket(customer_id, ticket_id):
    service_ticket = ServiceTicket.query.filter_by(id=ticket_id, customer_id=customer_id).first_or_404()
    return jsonify({
        "id": service_ticket.id,
        "VIN": service_ticket.VIN,
        "description": service_ticket.description,
        "service_date": service_ticket.service_date.isoformat(),
        "customer_id": service_ticket.customer_id
    })


@service_ticket_blueprint.route("/<int:ticket_id>", methods=["PUT"])
@token_required
def update_service_ticket(customer_id, ticket_id):
    service_ticket = ServiceTicket.query.filter_by(id=ticket_id, customer_id=customer_id).first_or_404()
    data = request.json
    service_ticket.VIN = data.get("VIN", service_ticket.VIN)
    service_ticket.description = data.get("description", service_ticket.description)
    db.session.commit()
    return jsonify({"message": "Service ticket updated successfully"}), 200


@service_ticket_blueprint.route("/<int:ticket_id>", methods=["DELETE"])
@token_required
def delete_service_ticket(customer_id, ticket_id):
    service_ticket = ServiceTicket.query.filter_by(id=ticket_id, customer_id=customer_id).first_or_404()
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({"message": "Service ticket deleted successfully"}), 200


@service_ticket_blueprint.route("/<int:ticket_id>/add-mechanics", methods=["PUT"])
def add_mechanics_to_service_ticket(ticket_id):
    # Fetch the service ticket
    service_ticket = ServiceTicket.query.get_or_404(ticket_id)

    # Get mechanic IDs to add or remove from the request payload
    data = request.json
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])

    # Add mechanics to the service ticket
    for mechanic_id in add_ids:
        mechanic = Mechanic.query.get(mechanic_id)
        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)

    # Remove mechanics from the service ticket
    for mechanic_id in remove_ids:
        mechanic = Mechanic.query.get(mechanic_id)
        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)

    db.session.commit()
    return jsonify({"message": "Mechanics updated successfully"}), 200




