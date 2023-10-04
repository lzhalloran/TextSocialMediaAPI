from flask import Blueprint, jsonify, request, abort
from main import db
from models.users import User
from schemas.user_schema import user_schema, users_schema, user_login_schema
from datetime import timedelta, date
from main import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.connections import Connection
from schemas.connection_schema import connection_schema, connections_schema

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
        return abort(404, description="Username does not exist")

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

## Connections route endpoints
# POST route endpoint - Request new connection
@users.route("/connections/request/<int:acceptor_id>", methods=["POST"])
@jwt_required()
def request_connection(acceptor_id):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    requestor = db.session.scalar(stmt)
    if not requestor:
        return abort(401, description="Invalid requesting user")

    # get other user by acceptor id, check if they exist
    stmt = db.select(User).filter_by(id=acceptor_id)
    acceptor = db.session.scalar(stmt)
    if not acceptor:
        return abort(404, description="Invalid accepting user")

    # if users are not the same id, if users are not already connected, create request
    if int(user_id) == acceptor_id:
        return abort(400, description="Requestor and Acceptor cannot be the same user")
    
    stmt = db.select(Connection).filter(
        ((Connection.requestor_id == int(user_id)) & (Connection.acceptor_id == acceptor_id)) | 
        ((Connection.requestor_id == acceptor_id) & (Connection.acceptor_id == int(user_id)))
    )
    connection = db.session.scalar(stmt)
    if connection:
        return abort(400, description="Connection already exists between these users")

    connection = Connection()
    connection.requestor_id = user_id
    connection.acceptor_id = acceptor_id
    connection.requested_date = date.today()
    
    db.session.add(connection)
    db.session.commit()
    
    return jsonify(connection_schema.dump(connection))

# GET route endpoint - Get connections
@users.route("/connections", methods=["GET"])
@jwt_required()
def get_connections():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")

    accepted_filter = request.args.get('accepted')
    if(accepted_filter == 'true'):
        stmt = db.select(Connection).filter(
            ((Connection.requestor_id == int(user_id)) | 
            (Connection.acceptor_id == int(user_id))) &
            (Connection.accepted_date.is_not(None))
        )
    elif(accepted_filter == 'false'):
        stmt = db.select(Connection).filter(
            ((Connection.requestor_id == int(user_id)) | 
            (Connection.acceptor_id == int(user_id))) &
            (Connection.accepted_date.is_(None))
        )
    else:
        stmt = db.select(Connection).filter(
            ((Connection.requestor_id == int(user_id)) | 
            (Connection.acceptor_id == int(user_id)))
        )
    connections_list = db.session.scalars(stmt)
    result = connections_schema.dump(connections_list)
    return jsonify(result)

# PUT route endpoint - Accept connection request
@users.route("/connections/accept/<int:requestor_id>", methods=["PUT"])
@jwt_required()
def accept_connection(requestor_id):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    acceptor = db.session.scalar(stmt)
    if not acceptor:
        return abort(401, description="Invalid accepting user")

    # get other user by requestor id, check if they exist
    stmt = db.select(User).filter_by(id=requestor_id)
    requestor = db.session.scalar(stmt)
    if not requestor:
        return abort(404, description="Invalid requesting user")

    if int(user_id) == requestor_id:
        return abort(400, description="Requestor and Acceptor cannot be the same user")
    
    stmt = db.select(Connection).filter_by(requestor_id=requestor_id, acceptor_id=int(user_id))
    connection = db.session.scalar(stmt)
    if not connection:
        return abort(404, description="Connection does not exist between these users")

    connection.accepted_date = date.today()
    
    db.session.commit()
    
    return jsonify(connection_schema.dump(connection))

# DELETE route endpoint - Delete connection
@users.route("/connections/delete/<int:other_user_id>", methods=["DELETE"])
@jwt_required()
def reject_connection(other_user_id):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")

    # get other user by other_user_id, check if they exist
    stmt = db.select(User).filter_by(id=other_user_id)
    other_user = db.session.scalar(stmt)
    if not other_user:
        return abort(404, description="Invalid other user")

    if int(user_id) == other_user_id:
        return abort(400, description="Requestor and Acceptor cannot be the same user")
    
    stmt = db.select(Connection).filter(
        ((Connection.requestor_id == int(user_id)) & (Connection.acceptor_id == other_user_id)) | 
        ((Connection.requestor_id == other_user_id) & (Connection.acceptor_id == int(user_id)))
    )
    connection = db.session.scalar(stmt)
    if not connection:
        return abort(404, description="Connection does not exist between these users")
    
    db.session.delete(connection)
    db.session.commit()

    return jsonify({'confirmation': 'The connection is deleted'})
    


## Exception Handling
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound
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

@users.errorhandler(NotFound)
def not_found_error(e):
    return jsonify({'error': e.description}), 404