from flask import Blueprint, jsonify, request, abort
from main import db
from models.users import User
from schemas.user_schema import user_schema, users_schema, user_login_schema
from datetime import timedelta
from main import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

users = Blueprint('users', __name__, url_prefix="/users")

# POST route endpoint - Register new user
@users.route("/register", methods=["POST"])
def user_register():
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
def user_login():
    user_fields = user_login_schema.load(request.json)
    stmt = db.select(User).filter_by(username=user_fields["username"])
    user = db.session.scalar(stmt)
    
    if not user or not bcrypt.check_password_hash(user.password, user_fields["password"]):
        return abort(401, description="Incorrect login details")

    expiry = timedelta(days=1)
    access_token = create_access_token(identity=str(user.id), expires_delta=expiry)
    
    return jsonify({"user":user.username, "token": access_token })

# GET route endpoint - Get user info and posts
@users.route("", methods=["GET"])
def user_page():
    stmt = db.select(User).filter_by(username=request.args.get('username'))
    user = db.session.scalar(stmt)

    if not user:
        return abort(400, description="Username does not exist")

    result = user_schema.dump(user)
    return jsonify(result)

# PUT route endpoint - Update user
@users.route("/", methods=["PUT"])
@jwt_required()
def user_update():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")
    
    user_fields = user_schema.load(request.json)

    user.username = user_fields["username"]
    user.email = user_fields["email"]
    user.password = bcrypt.generate_password_hash(user_fields["password"]).decode("utf-8")
    user.bio = user_fields["bio"]

    db.session.commit()

    expiry = timedelta(days=1)
    access_token = create_access_token(identity=str(user.id), expires_delta=expiry)
    
    return jsonify({"user":user.username, "token": access_token })

# DELETE route endpoint - Delete user
@users.route("/", methods=["DELETE"])
@jwt_required()
def user_delete():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({'confirmation': f'The user {user.username} is deleted'})


## Exception Handling
from werkzeug.exceptions import BadRequest, Unauthorized
from marshmallow.exceptions import ValidationError

@users.errorhandler(KeyError)
def key_error(e):
    return jsonify({'error': f'The field {e} is required'}), 400

@users.errorhandler(BadRequest)
def default_error(e):
    return jsonify({'error': e.description}), 400

@users.errorhandler(ValidationError)
def validation_error(e):
    return jsonify(e.messages), 400

@users.errorhandler(Unauthorized)
def unauthorized_error(e):
    return jsonify({'error': e.description}), 401