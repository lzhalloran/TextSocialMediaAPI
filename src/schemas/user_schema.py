from main import ma
from marshmallow.validate import Length
from models.users import User
from marshmallow import fields

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_only = ['password']
    posts = fields.List(fields.Nested("PostSchema", exclude=("user",)))

user_schema = UserSchema()
users_schema = UserSchema(many=True)

user_login_schema = UserSchema(only=('username', 'password'))