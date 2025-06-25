from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Inventory
from app.extensions import db  

class InventorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True


inventory_schema = InventorySchema(session=db.session)
inventories_schema = InventorySchema(many=True, session=db.session)