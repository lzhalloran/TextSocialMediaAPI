from main import ma
from marshmallow.validate import Length
from models.users import User

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
    password = ma.String(validate=Length(min=6,max=20))

user_schema = UserSchema()
users_schema = UserSchema(many=True)