from main import ma
from marshmallow import fields
from marshmallow.validate import Length

class PostSchema(ma.Schema):
    text = fields.String(required=True, validate=Length(min=1, max=1000))

    class Meta:
        ordered = True
        fields = ("id", "text", "created_time", "user", "comments")
    user = fields.Nested("UserSchema", only=("id", "username"))
    comments = fields.List(fields.Nested("CommentSchema"))

post_schema = PostSchema()
posts_schema = PostSchema(many=True)