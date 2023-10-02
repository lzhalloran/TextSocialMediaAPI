from main import ma
from marshmallow import fields

class PostSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ("id", "text", "created_time", "user")
    user = fields.Nested("UserSchema", only=("id", "username"))

post_schema = PostSchema()
posts_schema = PostSchema(many=True)