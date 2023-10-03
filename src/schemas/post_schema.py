from main import ma
from marshmallow import fields

class PostSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ("id", "text", "created_time", "user", "comments")
    user = fields.Nested("UserSchema", only=("id", "username"))
    comments = fields.List(fields.Nested("CommentSchema"))

post_schema = PostSchema()
posts_schema = PostSchema(many=True)