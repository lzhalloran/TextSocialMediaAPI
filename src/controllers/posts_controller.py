from flask import Blueprint, jsonify, request, abort
from main import db
from models.posts import Post
from models.users import User
from schemas.post_schema import post_schema, posts_schema
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

posts = Blueprint('posts', __name__, url_prefix="/posts")

# POST route endpoint
@posts.route("/", methods=["POST"])
@jwt_required()
def create_post():
    post_fields = post_schema.load(request.json)

    new_post = Post()
    new_post.text = post_fields["text"]
    new_post.created_time = datetime.now()

    db.session.add(new_post)
    db.session.commit()

    return jsonify(post_schema.dump(new_post))

# GET route endpoint
@posts.route("/", methods=["GET"])
@jwt_required()
def get_posts():
    stmt = db.select(Post)
    posts_list = db.session.scalars(stmt)
    result = posts_schema.dump(posts_list)
    return jsonify(result)

# DELETE route endpoint
@posts.route("/<int:id>/", methods=["DELETE"])
@jwt_required()
def delete_post(id):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")
    
    stmt = db.select(Post).filter_by(id=id)
    post = db.session.scalar(stmt)

    if not post:
        return abort(400, description="Post does not exist")
    
    db.session.delete(post)
    db.session.commit()

    return jsonify(post_schema.dump(post))

