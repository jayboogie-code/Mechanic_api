import unittest
from app import create_app, db
from app.models import Customer, ServiceTicket
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

class TestCustomerBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.TestingConfig")  # Use a testing configuration
        self.client = self.app.test_client()  # Create a test client
        with self.app.app_context():
            db.drop_all()  # Drop all tables to clear old data
            db.create_all()  # Set up the database for testing

            # Create a test customer with a unique email
            self.test_customer = Customer(
                name="John Doe",
                email="unique_test@example.com",  # Ensure unique email
                password_hash=generate_password_hash("password123"),
                phone="1234567890"
            )
            db.session.add(self.test_customer)
            db.session.commit()

            # Create a test service ticket associated with the customer
            self.service_ticket = ServiceTicket(
                VIN="1HGCM82633A123456",
                description="Oil change",
                customer_id=self.test_customer.id,  # Associate with the test customer
                service_date=datetime.now(timezone.utc)  # Use timezone-aware datetime
            )
            db.session.add(self.service_ticket)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up the database after each test

    def get_token(self):
        """Helper method to log in and retrieve a token."""
        response = self.client.post("/customers/login", json={
            "email": "unique_test@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        return response.json["token"]

    def test_customer_login_success(self):
        response = self.client.post("/customers/login", json={
            "email": "unique_test@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)

    def test_customer_login_failure(self):
        response = self.client.post("/customers/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)  # Update expected status code
        self.assertIn("message", response.json)

   

    def test_get_my_tickets_unauthorized(self):
        response = self.client.get("/customers/my-tickets")  # No Authorization header
        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json)

    def test_get_customers_success(self):
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("customers", response.json)  # Check for 'customers' key
        self.assertIsInstance(response.json["customers"], list)  # Validate the list of customers
        self.assertEqual(len(response.json["customers"]), 1)
        self.assertEqual(response.json["customers"][0]["name"], "John Doe")

    def test_register_customer_success(self):
        response = self.client.post("/customers/register", json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "9876543210",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Customer registered successfully")

    def test_register_customer_failure(self):
        response = self.client.post("/customers/register", json={
            "name": "",
            "email": "",
            "phone": "",
            "password": ""
        })  # Missing required fields
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json)

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