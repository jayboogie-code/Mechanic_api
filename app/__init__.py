from flask import Flask
from app.extensions import db, ma, limiter, cache, migrate  
from app.blueprints.customers import customers_bp
from app.blueprints.mechanic import mechanics_bp
from app.blueprints.service_ticket import service_ticket_bp
from app.blueprints.inventory import inventory_bp

def create_app(config_class="config.DevelopmentConfig"):
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

    return app