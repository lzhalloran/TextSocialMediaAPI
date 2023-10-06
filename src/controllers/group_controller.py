from flask import Blueprint, jsonify, request, abort
from main import db
from models.groups import Group
from schemas.group_schema import group_schema, groups_schema
from models.memberships import Membership
from schemas.membership_schema import membership_schema, memberships_schema
from datetime import date
from flask_jwt_extended import jwt_required, get_jwt_identity

groups = Blueprint('groups', __name__, url_prefix="/groups")

# POST route endpoint - Create new group
@groups.route("/", methods=["POST"])
@jwt_required()
def create_group():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    requestor = db.session.scalar(stmt)
    if not requestor:
        return abort(401, description="Invalid requesting user")

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

    # get group by group name, check if they exist
    stmt = db.select(Group).filter_by(name=group_name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group does not exist")

    membership = Membership()
    membership.user_id = user_id
    membership.group_id = group.id
    membership.requested_date = date.today()
    membership.accepted_date = date.today()
    
    db.session.add(membership)
    db.session.commit()

    result = group_schema.dump(group)
    return jsonify(result)

# GET route endpoint - Get group info, posts
@groups.route("/<string:name>", methods=["GET"])
@jwt_required()
def group_page(name):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")

    stmt = db.select(Group).filter_by(name=name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group with that name does not exist")
    
    stmt = db.select(Membership).filter(
        (Membership.group_id == group.id) &
        (Membership.user_id == int(user_id))
    )
    membership = db.session.scalar(stmt)
    if not membership or (membership.accepted_date is None):
        return abort(401, description="Current user is not member of this group")
    
    result = group_schema.dump(group)
    return jsonify(result)

# PUT route endpoint - Update group info
@groups.route("/<string:name>", methods=["PUT"])
@jwt_required()
def update_group(name):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")

    stmt = db.select(Group).filter_by(name=name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group with that name does not exist")
    
    stmt = db.select(Membership).filter(
        (Membership.group_id == group.id) &
        (Membership.user_id == int(user_id))
    )
    admin_membership = db.session.scalar(stmt)
    if not admin_membership.admin:
        return abort(401, description="Current user is not admin of this group")

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
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")

    stmt = db.select(Group).filter_by(name=name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group with that name does not exist")
    
    stmt = db.select(Membership).filter(
        (Membership.group_id == group.id) &
        (Membership.user_id == int(user_id))
    )
    admin_membership = db.session.scalar(stmt)
    if not admin_membership.admin:
        return abort(401, description="Current user is not admin of this group")
    
    db.session.delete(group)
    db.session.commit()

    return jsonify({'confirmation': f'The group {group.name} is deleted'})

## Membership route endpoints
# POST route endpoint - Request new membership
@groups.route("/<string:group_name>/memberships", methods=["POST"])
@jwt_required()
def request_membership(group_name):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    requestor = db.session.scalar(stmt)
    if not requestor:
        return abort(401, description="Invalid requesting user")

    # get group by group name, check if they exist
    stmt = db.select(Group).filter_by(name=group_name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group does not exist")
    
    stmt = db.select(Membership).filter(
        (Memborship.user_id == int(user_id)) & (Membership.group_id == group.id)
    )
    membership = db.session.scalar(stmt)
    if membership:
        return abort(400, description="Membership already exists for this user and group")

    membership = Membership()
    membership.user_id = user_id
    membership.group_id = group.id
    membership.requested_date = date.today()
    
    db.session.add(membership)
    db.session.commit()
    
    return jsonify(membership_schema.dump(membership))

# GET route endpoint - Get memberships
@groups.route("/<string:group_name>/memberships", methods=["GET"])
@jwt_required()
def get_membership(group_name):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")

    # get group by group name, check if they exist
    stmt = db.select(Group).filter_by(name=group_name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group does not exist")

    stmt = db.select(Membership).filter(
        (Membership.group_id == group.id) &
        (Membership.user_id == int(user_id))
    )
    admin_membership = db.session.scalar(stmt)
    if not admin_membership.admin:
        return abort(401, description="Current user is not admin of this group")

    accepted_filter = request.args.get('accepted')
    if(accepted_filter == 'true'):
        stmt = db.select(Membership).filter(
            (Membership.group_id == group.id) &
            (Membership.accepted_date.is_not(None))
        )
    elif(accepted_filter == 'false'):
        stmt = db.select(Membership).filter(
            (Membership.group_id == group.id) &
            (Membership.accepted_date.is_(None))
        )
    else:
        stmt = db.select(Membership).filter(
            (Membership.group_id == group.id)
        )
    memberships_list = db.session.scalars(stmt)
    result = memberships_schema.dump(memberships_list)
    return jsonify(result)

# PUT route endpoint - Accept membership request
@groups.route("/<string:group_name>/memberships/<string:user_name>", methods=["PUT"])
@jwt_required()
def accept_membership(group_name, user_name):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")

    # get group by group name, check if they exist
    stmt = db.select(Group).filter_by(name=group_name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group does not exist")

    stmt = db.select(Membership).filter(
        (Membership.group_id == group.id) &
        (Membership.user_id == int(user_id))
    )
    admin_membership = db.session.scalar(stmt)
    if not admin_membership.admin:
        return abort(401, description="Current user is not admin of this group")

    # get other user by user_name, check if they exist
    stmt = db.select(User).filter_by(username=user_name)
    requestor = db.session.scalar(stmt)
    if not requestor:
        return abort(404, description="Invalid requesting user")
    
    stmt = db.select(Membership).filter_by(user_id=requestor.id, group_id=group.id)
    membership = db.session.scalar(stmt)
    if not membership:
        return abort(404, description="Membership does not exist for this user and group")

    membership.accepted_date = date.today()
    
    db.session.commit()
    
    return jsonify(membership_schema.dump(membership))

# DELETE route endpoint - Delete membership
@groups.route("/<string:group_name>/memberships/<string:user_name>", methods=["DELETE"])
@jwt_required()
def reject_membership(group_name, user_name):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")

    # get group by group name, check if they exist
    stmt = db.select(Group).filter_by(name=group_name)
    group = db.session.scalar(stmt)
    if not group:
        return abort(404, description="Group does not exist")

    stmt = db.select(Membership).filter(
        (Membership.group_id == group.id) &
        (Membership.user_id == int(user_id))
    )
    admin_membership = db.session.scalar(stmt)
    if not admin_membership.admin:
        return abort(401, description="Current user is not admin of this group")

    # get other user by user_name, check if they exist
    stmt = db.select(User).filter_by(username=user_name)
    requestor = db.session.scalar(stmt)
    if not requestor:
        return abort(404, description="Invalid requesting user")
    
    stmt = db.select(Membership).filter_by(user_id=requestor.id, group_id=group.id)
    membership = db.session.scalar(stmt)
    if not membership:
        return abort(404, description="Membership does not exist for this user and group")
    
    db.session.delete(membership)
    db.session.commit()

    return jsonify({'confirmation': 'The membership is deleted'})

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