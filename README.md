# Mechanic API

Mechanic API is a Flask-based application designed to manage mechanics, customers, service tickets, and inventory for a mechanic shop. It provides endpoints for authentication, CRUD operations, and relationships between entities.

## Features

- **Authentication**: Token-based authentication for customers and mechanics.
- **Customer Management**: Register, login, and manage customer service tickets.
- **Mechanic Management**: Register, login, and manage mechanics.
- **Service Tickets**: Create, update, delete, and manage service tickets.
- **Inventory Management**: Manage inventory items and associate them with service tickets.

## Project Structure

### Key Files

- **`app.py`**: Entry point for the application.
- **`app/models.py`**: Defines database models for `Customer`, `Mechanic`, `ServiceTicket`, and `Inventory`.
- **`app/auth/`**: Contains authentication utilities and decorators.
- **`app/blueprints/`**: Contains route definitions for different entities.
- **`config.py`**: Configuration settings for different environments.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mechanic-api
2. Create a virtual environment:

  python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Set up the database
Update the SQLALCHEMY_DATABASE_URI in config.py with your database credentials.
Run migrations:

flask db upgrade
5. Start the application:
python app.py

API Endpoints
Customer Routes
POST /customers/register: Register a new customer.
POST /customers/login: Login as a customer.
GET /customers/my-tickets: Get all service tickets for the logged-in customer.
Mechanic Routes
POST /mechanics/register: Register a new mechanic.
POST /mechanics/login: Login as a mechanic.
GET /mechanics/statistics: Get statistics for mechanics.
Service Ticket Routes
POST /service-tickets/: Create a new service ticket.
GET /service-tickets/<ticket_id>: Get details of a service ticket.
PUT /service-tickets/<ticket_id>: Update a service ticket.
DELETE /service-tickets/<ticket_id>: Delete a service ticket.

Inventory Routes
POST /inventory/: Create a new inventory item.
GET /inventory/: Get all inventory items.
PUT /inventory/<id>: Update an inventory item.
DELETE /inventory/<id>: Delete an inventory item.

Postman Collection
A Postman collection is provided in Mechanic API.postman_collection.json for testing the API.
 
