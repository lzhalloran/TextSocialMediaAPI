from main import ma
from marshmallow import fields

class CommentSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ("id", "text", "created_time", "user")
    user = fields.Nested("UserSchema", only=("id", "username"))

comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)