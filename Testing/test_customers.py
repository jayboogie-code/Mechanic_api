import unittest
from app import create_app, db
from app.models import Customer, ServiceTicket
from werkzeug.security import generate_password_hash

class TestCustomerBlueprint(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.TestingConfig")  # Use a testing configuration
        self.client = self.app.test_client()  # Create a test client
        with self.app.app_context():
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
                customer_id=self.test_customer.id
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
            "email": "test@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        return response.json["token"]

    def test_customer_login_success(self):
        response = self.client.post("/customers/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)

    def test_customer_login_failure(self):
        response = self.client.post("/customers/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json)

    def test_get_my_tickets_success(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.get("/customers/my-tickets", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]["VIN"], "1HGCM82633A123456")

    def test_get_my_tickets_unauthorized(self):
        response = self.client.get("/customers/my-tickets")  # No Authorization header
        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json)

    def test_get_customers_success(self):
        response = self.client.get("/customers/?page=1&per_page=10")
        self.assertEqual(response.status_code, 200)
        self.assertIn("customers", response.json)
        self.assertIn("total", response.json)
        self.assertIn("pages", response.json)
        self.assertEqual(len(response.json["customers"]), 1)

    def test_register_customer_success(self):
        response = self.client.post("/customers/register", json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "password123",
            "phone": "9876543210"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Customer registered successfully")

    def test_register_customer_failure(self):
        response = self.client.post("/customers/register", json={
            "name": "John Doe",
            "email": "test@example.com",  # Email already exists
            "password": "password123",
            "phone": "1234567890"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Email already exists")

    def test_create_service_ticket_success(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.post("/customers/create-ticket", json={
            "VIN": "2HGCM82633A654321",
            "description": "Brake replacement"
        }, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Service ticket created successfully")

    def test_create_service_ticket_failure(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.post("/customers/create-ticket", json={
            "VIN": "",
            "description": ""
        }, headers=headers)  # Missing required fields
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "VIN and description are required")

if __name__ == "__main__":
    unittest.main()