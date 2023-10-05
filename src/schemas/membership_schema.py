from main import ma
from marshmallow import fields

class MembershipSchema(ma.Schema):
    requested_date = fields.Date(required=True)
    accepted_date = fields.Date(required=False)
    admin = fields.Boolean(required=False)

    class Meta:
        ordered = True
        fields = ("id", "requested_date", "accepted_date", "admin", "user", "group")
    user = fields.Nested("UserSchema", only=("id", "username"))
    group = fields.Nested("GroupSchema", only=("id", "name"))

membership_schema = MembershipSchema()
memberships_schema = MembershipSchema(many=True)