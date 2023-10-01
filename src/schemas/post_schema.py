from main import ma

class PostSchema(ma.Schema):
    class Meta:
        fields = ("id", "text", "created_time")

post_schema = PostSchema()
posts_schema = PostSchema(many=True)