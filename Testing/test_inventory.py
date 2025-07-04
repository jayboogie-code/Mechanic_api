import unittest
from app import create_app, db
from app.models import Inventory, Mechanic, ServiceTicket, Customer  # Import Customer model
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone  # Import datetime and timezone

class TestInventoryBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.TestingConfig")  # Use a testing configuration
        self.client = self.app.test_client()  # Create a test client
        with self.app.app_context():
            db.drop_all()  # Drop all tables to clear old data
            db.create_all()  # Set up the database for testing

            # Create a test mechanic
            self.test_mechanic = Mechanic(
                name="Jane Doe",
                email="mechanic@example.com",
                phone="1234567890",
                salary=50000,
                password_hash=generate_password_hash("password123")
            )
            db.session.add(self.test_mechanic)
            db.session.commit()

            # Create a test customer
            self.test_customer = Customer(
                name="Inventory Tester",
                email="inventory@example.com",
                phone="5555555555",
                password_hash=generate_password_hash("securepassword")
            )
            db.session.add(self.test_customer)
            db.session.commit()

            # Create a test inventory item
            self.inventory_item = Inventory(
                name="Brake Pads",
                price=49.99
            )
            db.session.add(self.inventory_item)
            db.session.commit()

            # Create a test service ticket linked to customer_id
            self.service_ticket = ServiceTicket(
                VIN="1HGCM82633A123456",
                description="Oil change",
                service_date=datetime.now(timezone.utc),  # Use timezone-aware datetime
                customer_id=self.test_customer.id  # Associate with customer
            )
            db.session.add(self.service_ticket)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up the database after each test

    def get_mechanic_token(self):
        """Helper method to log in and retrieve a mechanic token."""
        response = self.client.post("/mechanics/login", json={
            "email": "mechanic@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        return response.json["token"]

    def test_create_inventory_success(self):
        response = self.client.post("/inventory/", json={
            "name": "Brake Fluid",
            "price": 15.99
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("name", response.json)
        self.assertEqual(response.json["name"], "Brake Fluid")
        self.assertIn("price", response.json)
        self.assertEqual(response.json["price"], 15.99)

    def test_create_inventory_failure(self):
        response = self.client.post("/inventory/", json={
            "name": "",  # Invalid name
            "price": 15.99
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json)
        self.assertIn("name", response.json["errors"])

    def test_get_inventories_success(self):
        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "Brake Pads")

    

    def test_update_inventory_failure(self):
        response = self.client.put("/inventory/999", json={
            "name": "Updated Brake Pads",
            "price": 59.99
        })  # Non-existent inventory ID
        self.assertEqual(response.status_code, 404)

    
if __name__ == "__main__":
    unittest.main()