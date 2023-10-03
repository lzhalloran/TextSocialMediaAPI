from main import ma
from marshmallow.validate import Length
from models.users import User
from marshmallow import fields

class UserSchema(ma.SQLAlchemyAutoSchema):
    username = fields.String(required=True, validate=Length(min=1, max=20))
    email = fields.String(required=True, validate=Length(min=3, max=254))
    password = fields.String(required=True, validate=Length(min=1))
    bio = fields.String(required=True)

    class Meta:
        model = User
        load_only = ['password']
    posts = fields.List(fields.Nested("PostSchema", exclude=("user",)))

user_schema = UserSchema()
users_schema = UserSchema(many=True)

user_login_schema = UserSchema(only=('username', 'password'))