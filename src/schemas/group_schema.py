from main import ma
from models.groups import Group
from marshmallow import fields
from marshmallow.validate import Length

class GroupSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True, validate=Length(min=1, max=50))
    bio = fields.String(required=False)

    class Meta:
        model = Group
    posts = fields.List(fields.Nested("PostSchema", exclude=("group",)))

group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)