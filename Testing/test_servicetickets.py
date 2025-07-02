import unittest
from app import create_app, db
from app.models import Customer, ServiceTicket, Mechanic
from werkzeug.security import generate_password_hash

class TestServiceTicketBlueprint(unittest.TestCase):
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

            # Create test mechanics
            self.mechanic1 = Mechanic(name="Jane Smith", email="jane@example.com", phone="1234567890", salary=50000)
            self.mechanic2 = Mechanic(name="John Smith", email="john@example.com", phone="1234567890", salary=60000)
            db.session.add(self.mechanic1)
            db.session.add(self.mechanic2)
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

    def test_create_service_ticket_failure(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.post("/service-tickets/", json={
            "VIN": "",
            "description": ""
        }, headers=headers)  # Missing required fields
        self.assertEqual(response.status_code, 400)

    def test_get_service_ticket_success(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.get(f"/service-tickets/{self.service_ticket.id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("VIN", response.json)
        self.assertEqual(response.json["VIN"], "1HGCM82633A123456")

    def test_get_service_ticket_failure(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.get("/service-tickets/999", headers=headers)  # Non-existent ticket ID
        self.assertEqual(response.status_code, 404)

    def test_update_service_ticket_success(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.put(f"/service-tickets/{self.service_ticket.id}", json={
            "VIN": "2HGCM82633A654321",
            "description": "Brake replacement"
        }, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Service ticket updated successfully")

    def test_update_service_ticket_failure(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.put("/service-tickets/999", json={
            "VIN": "2HGCM82633A654321",
            "description": "Brake replacement"
        }, headers=headers)  # Non-existent ticket ID
        self.assertEqual(response.status_code, 404)

    def test_delete_service_ticket_success(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.delete(f"/service-tickets/{self.service_ticket.id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Service ticket deleted successfully")

    def test_delete_service_ticket_failure(self):
        headers = {"Authorization": "Bearer " + self.get_token()}
        response = self.client.delete("/service-tickets/999", headers=headers)  # Non-existent ticket ID
        self.assertEqual(response.status_code, 404)

    def test_add_mechanics_to_service_ticket_success(self):
        response = self.client.put(f"/service-tickets/{self.service_ticket.id}/add-mechanics", json={
            "add_ids": [self.mechanic1.id, self.mechanic2.id],
            "remove_ids": []
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Mechanics updated successfully")

    def test_add_mechanics_to_service_ticket_failure(self):
        response = self.client.put("/service-tickets/999/add-mechanics", json={
            "add_ids": [self.mechanic1.id],
            "remove_ids": []
        })  # Non-existent ticket ID
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()