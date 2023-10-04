from main import ma
from marshmallow import fields

class ConnectionSchema(ma.Schema):
    requested_date = fields.Date(required=True)
    accepted_date = fields.Date(required=False)
    

    class Meta:
        ordered = True
        fields = ("id", "requested_date", "accepted_date", "requestor", "acceptor")
    requestor = fields.Nested("UserSchema", only=("id", "username"))
    acceptor = fields.Nested("UserSchema", only=("id", "username"))

connection_schema = ConnectionSchema()
connections_schema = ConnectionSchema(many=True)