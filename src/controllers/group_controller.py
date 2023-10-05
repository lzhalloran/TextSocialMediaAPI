from flask import Blueprint, jsonify, request, abort
from main import db
from models.groups import Group
from schemas.group_schema import group_schema, groups_schema
from flask_jwt_extended import jwt_required, get_jwt_identity

groups = Blueprint('groups', __name__, url_prefix="/groups")

# POST route endpoint - Create new group
@groups.route("/", methods=["POST"])
@jwt_required()
def create_group():
    group_fields = group_schema.load(request.json)
    stmt = db.select(Group).filter_by(name=group_fields["name"])
    group = db.session.scalar(stmt)

    if group:
        return abort(400, description="Group name already in use")
    
    group = Group()
    group.name = group_fields["name"]
    group.bio = group_fields["bio"]

    db.session.add(group)
    db.session.commit()

    result = group_schema.dump(group)
    return jsonify(result)

# GET route endpoint - Get group info, posts
@groups.route("/<string:name>", methods=["GET"])
@jwt_required()
def group_page(name):
    stmt = db.select(Group).filter_by(name=name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group with that name does not exist")
    
    result = group_schema.dump(group)
    return jsonify(result)

# PUT route endpoint - Update group info
@groups.route("/<string:name>", methods=["PUT"])
@jwt_required()
def update_group(name):
    stmt = db.select(Group).filter_by(name=name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group with that name does not exist")

    group_fields = group_schema.load(request.json)

    group.name = group_fields["name"]
    group.bio = group_fields["bio"]

    db.session.commit()

    result = group_schema.dump(group)
    return jsonify(result)

# DELETE route endpoint - Delete group
@groups.route("/<string:name>", methods=["DELETE"])
@jwt_required()
def delete_group(name):
    stmt = db.select(Group).filter_by(name=name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group with that name does not exist")
    
    db.session.delete(group)
    db.session.commit()

    return jsonify({'confirmation': f'The group {group.name} is deleted'})



## Exception Handling
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound, MethodNotAllowed
from marshmallow.exceptions import ValidationError

@groups.errorhandler(KeyError)
def key_error(e):
    return jsonify({'error': f'The field {e} is required'}), 400

@groups.errorhandler(BadRequest)
def default_error(e):
    return jsonify({'error': e.description}), 400

@groups.errorhandler(ValidationError)
def validation_error(e):
    return jsonify(e.messages), 400

@groups.errorhandler(Unauthorized)
def unauthorized_error(e):
    return jsonify({'error': e.description}), 401

@groups.errorhandler(NotFound)
def not_found_error(e):
    return jsonify({'error': e.description}), 404

@groups.errorhandler(MethodNotAllowed)
def method_not_allowed_error(e):
    return jsonify({'error': e.description}), 405