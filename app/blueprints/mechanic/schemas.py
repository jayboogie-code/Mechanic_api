from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from app.models import Mechanic
from app.extensions import db  

class MechanicSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True

    email = fields.Email(required=True)
    phone = fields.Str(required=True)
    password = fields.Str(load_only=True)  # Mark password as load_only to exclude it from updates
    password_hash = fields.Str(dump_only=True)  # Exclude password_hash from validation

mechanic_schema = MechanicSchema(session=db.session)
mechanics_schema = MechanicSchema(many=True, session=db.session)