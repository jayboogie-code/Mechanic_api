import unittest
from app import create_app, db
from app.models import Customer, ServiceTicket, Mechanic
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

class TestServiceTicketBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.TestingConfig")  # Use a testing configuration
        self.client = self.app.test_client()  # Create a test client
        with self.app.app_context():
            db.drop_all()  # Drop all tables to clear old data
            db.create_all()  # Set up the database for testing

            # Create a test customer
            self.test_customer = Customer(
                name="John Doe",
                email="test@example.com",
                password_hash=generate_password_hash("password123"),
                phone="1234567890"
            )
            db.session.add(self.test_customer)
            db.session.commit()

            # Create a test service ticket
            self.service_ticket = ServiceTicket(
                VIN="1HGCM82633A123456",
                description="Oil change",
                customer_id=self.test_customer.id,
                service_date=datetime.now(timezone.utc)
            )
            db.session.add(self.service_ticket)
            db.session.commit()

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

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up the database after each test

    def get_token(self):
        """Helper method to log in and retrieve a token."""
        response = self.client.post("/customers/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        return response.json["token"]

    def test_create_service_ticket_success(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.post("/service-tickets/", json={
            "VIN": "2HGCM82633A654321",
            "description": "Brake replacement"
        }, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Service ticket created successfully")

   

   

    

if __name__ == "__main__":
    unittest.main()