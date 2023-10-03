from main import ma
from marshmallow import fields
from marshmallow.validate import Length

class CommentSchema(ma.Schema):
    text = fields.String(required=True, validate=Length(min=1, max=1000))

    class Meta:
        ordered = True
        fields = ("id", "text", "created_time", "user")
    user = fields.Nested("UserSchema", only=("id", "username"))

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)