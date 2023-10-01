from flask import Blueprint, jsonify, request
from main import db
from models.users import User

users = Blueprint('users', __name__, url_prefix="/users")

# POST route endpoint - Register new user
@users.route("/register", methods=["POST"])
def users_register():
    user_fields = user_schema.load(request.json)
    stmt = db.select(User).filter_by(username=user_fields["username"])
    user = db.session.scalar(stmt)

    if user:
        return abort(400, description="Username already in use")

    user = User()
    user.username = user_fields["username"]
    user.email = user_fields["email"]
    user.password = bcrypt.generate_password_hash(user_fields["password"]).decode("utf-8")
    user.bio = user_fields["bio"]
    
    db.session.add(user)
    db.session.commit()

    expiry = timedelta(days=1)
    access_token = create_access_token(identity=str(user.id), expires_delta=expiry)
    
    return jsonify({"user":user.username, "token": access_token })

# POST route endpoint - Login existing user
@users.route("/login", methods=["POST"])
def users_login():
    user_fields = user_schema.load(request.json)
    stmt = db.select(User).filter_by(username=user_fields["username"])
    user = db.session.scalar(stmt)
    
    if not user or not bcrypt.check_password_hash(user.password, user_fields["password"]):
        return abort(401, description="Incorrect login details")

    expiry = timedelta(days=1)
    access_token = create_access_token(identity=str(user.id), expires_delta=expiry)
    
    return jsonify({"user":user.username, "token": access_token })