from datetime import datetime
from typing import List  # Import list for type hints
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .extensions import db
from werkzeug.security import check_password_hash
from sqlalchemy import Float

class Mechanic(db.Model):  
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    salary: Mapped[float] = mapped_column(db.Float(), nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(256), nullable=False)  # Add password_hash field

    # Many-to-Many Relationship with ServiceTicket
    service_tickets: Mapped[list["ServiceTicket"]] = relationship(
        "ServiceTicket",
        secondary="mechanic_service_ticket",
        back_populates="mechanics"
    )

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


class ServiceTicket(db.Model):  
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(17), nullable=False)  
    description: Mapped[str] = mapped_column(db.String(300), nullable=False)
    service_date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"), nullable=False)

    # Relationship with Customer
    customer: Mapped["Customer"] = relationship("Customer", back_populates="service_tickets")

    # Many-to-Many Relationship with Mechanic
    mechanics: Mapped[list["Mechanic"]] = relationship(
        "Mechanic",
        secondary="mechanic_service_ticket",
        back_populates="service_tickets"
    )

    # Many-to-Many Relationship with Inventory
    inventory_items: Mapped[list["Inventory"]] = relationship(
        "Inventory",
        secondary="inventory_service_ticket",
        back_populates="service_tickets"
    )


# Junction table for Mechanic and ServiceTicket
mechanic_service_ticket = db.Table(
    "mechanic_service_ticket",
    db.Column("mechanic_id", db.Integer, db.ForeignKey("mechanics.id"), primary_key=True),
    db.Column("service_ticket_id", db.Integer, db.ForeignKey("service_tickets.id"), primary_key=True)
)


# Junction table for Inventory and ServiceTicket
inventory_service_ticket = db.Table(
    "inventory_service_ticket",
    db.Column("inventory_id", db.Integer, db.ForeignKey("inventory.id"), primary_key=True),
    db.Column("service_ticket_id", db.Integer, db.ForeignKey("service_tickets.id"), primary_key=True)
)


class Customer(db.Model):  
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(256), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(15), nullable=False)

    # Relationship with ServiceTicket
    service_tickets: Mapped[list["ServiceTicket"]] = relationship("ServiceTicket", back_populates="customer")

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)


class Inventory(db.Model): 
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    price: Mapped[float] = mapped_column(db.Float(), nullable=False)

    # Many-to-Many Relationship with ServiceTicket
    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        "ServiceTicket",
        secondary="inventory_service_ticket",
        back_populates="inventory_items"
    )