from marshmallow import Schema, fields

class CustomerSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    phone = fields.Str(required=True)

login_schema = CustomerSchema(only=("email", "password"))
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)