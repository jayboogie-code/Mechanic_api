import unittest
from app import create_app, db
from app.models import Mechanic, ServiceTicket, Customer
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

class TestMechanicBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.TestingConfig")  # Use a testing configuration
        self.client = self.app.test_client()  # Create a test client
        with self.app.app_context():
            db.drop_all()  # Drop all tables to clear old data
            db.create_all()  # Set up the database for testing

            # Create a test customer (needed because ServiceTicket.customer_id is NOT NULL)
            self.test_customer = Customer(
                name="Alice Example",
                email="alice@example.com",
                phone="5555555555",
                password_hash=generate_password_hash("securepass123")
            )
            db.session.add(self.test_customer)
            db.session.commit()

            # Create a test service ticket associated with the test customer
            self.service_ticket = ServiceTicket(
                VIN="1HGCM82633A123456",
                description="Oil change",
                customer_id=self.test_customer.id,  # Associate with customer
                service_date=datetime.now(timezone.utc)  # Use timezone-aware datetime
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

    def get_mechanic_token(self):
        """Helper method to log in and retrieve a mechanic token."""
        response = self.client.post("/mechanics/login", json={
            "email": "mechanic@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        return response.json["token"]

    def test_mechanic_login_success(self):
        response = self.client.post("/mechanics/login", json={
            "email": "mechanic@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)

    def test_mechanic_login_failure(self):
        response = self.client.post("/mechanics/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json)

    def test_mechanic_statistics_success(self):
        headers = {"Authorization": "Bearer " + self.get_mechanic_token()}
        response = self.client.get("/mechanics/statistics", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_mechanic_statistics_unauthorized(self):
        response = self.client.get("/mechanics/statistics")  # No Authorization header
        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json)

    def test_get_mechanics_success(self):
        response = self.client.get("/mechanics/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["name"], "Jane Doe")


    def test_update_mechanic_failure(self):
        response = self.client.put("/mechanics/999", json={
            "name": "Jane Updated",
            "phone": "9876543210",
            "salary": 60000
        })  # Non-existent mechanic ID
        self.assertEqual(response.status_code, 404)

   

    def test_delete_mechanic_failure(self):
        response = self.client.delete("/mechanics/999")  # Non-existent mechanic ID
        self.assertEqual(response.status_code, 404)

   

    def test_register_mechanic_failure(self):
        response = self.client.post("/mechanics/register", json={
            "name": "Jane Doe",
            "email": "mechanic@example.com",  # Email already exists
            "phone": "1234567890",
            "salary": 55000,
            "password": "password123"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Email already exists")

if __name__ == "__main__":
    unittest.main()