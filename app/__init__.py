from flask import Flask
from app.extensions import db, ma, limiter, cache, migrate  
from app.blueprints.customers import customers_bp
from app.blueprints.mechanic import mechanics_bp
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.inventory import inventory_bp
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def create_app(config_class="config.ProductionConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)
  
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    cache.init_app(app, config={"CACHE_TYPE": "SimpleCache"})
    limiter.init_app(app)
    migrate.init_app(app, db)  

    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_ticket_bp, url_prefix="/service-tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    # Swagger UI setup
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.yaml'  # Path to your Swagger YAML file
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app