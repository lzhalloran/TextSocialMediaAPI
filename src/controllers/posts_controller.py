from flask import Blueprint, jsonify, request, abort
from main import db
from models.posts import Post
from models.users import User
from models.comments import Comment
from schemas.post_schema import post_schema, posts_schema
from schemas.comment_schema import comment_schema, comments_schema
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

posts = Blueprint('posts', __name__, url_prefix="/posts")

# POST route endpoint
@posts.route("/", methods=["POST"])
@jwt_required()
def create_post():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")

    post_fields = post_schema.load(request.json)

    new_post = Post()
    new_post.text = post_fields["text"]
    new_post.created_time = datetime.now()
    new_post.user_id = user_id

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

# PUT route endpoint
@posts.route("/<int:id>/", methods=["PUT"])
@jwt_required()
def update_post(id):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")
    
    stmt = db.select(Post).filter_by(id=id)
    post = db.session.scalar(stmt)
    if not post:
        return abort(404, description="Post does not exist")
    
    if post.user.id != int(user_id):
        return abort(401, description=f"User ({user_id}) cannot update other user ({post.user.id}) posts")
    
    post_fields = post_schema.load(request.json)

    post.text = post_fields["text"]

    db.session.commit()

    return jsonify(post_schema.dump(post))

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
        return abort(404, description="Post does not exist")
    
    if post.user.id != int(user_id):
        return abort(401, description=f"User ({user_id}) cannot delete other user ({post.user.id}) posts")

    db.session.delete(post)
    db.session.commit()
    return jsonify({'confirmation': f'The post {id} is deleted'})

## Comment route endpoints
# POST route endpoint - new comment
@posts.route("<int:id>/comments", methods=["POST"])
@jwt_required()
def create_comment(id):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")
    
    stmt = db.select(Post).filter_by(id=id)
    post = db.session.scalar(stmt)
    if not post:
        return abort(400, description="Post does not exist")

    comment_fields = comment_schema.load(request.json)

    new_comment = Comment()
    new_comment.text = comment_fields["text"]
    new_comment.created_time = datetime.now()
    new_comment.user_id = user_id
    new_comment.post = post

    db.session.add(new_comment)
    db.session.commit()

    return jsonify(comment_schema.dump(new_comment))

# DELETE route endpoint - delete comment
@posts.route("<int:post_id>/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(post_id, comment_id):
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return abort(401, description="Invalid user")
    
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    if not comment:
        return abort(400, description="Comment does not exist")
    
    if comment.user.id != int(user_id):
        return abort(401, description=f"User ({user_id}) cannot delete other user ({comment.user.id}) comments")

    db.session.delete(comment)
    db.session.commit()

    return jsonify(comment_schema.dump(comment))

## Exception Handling
from werkzeug.exceptions import BadRequest, Unauthorized
from marshmallow.exceptions import ValidationError

@posts.errorhandler(KeyError)
def key_error(e):
    return jsonify({'error': f'The field {e} is required'}), 400

@posts.errorhandler(BadRequest)
def default_error(e):
    return jsonify({'error': e.description}), 400

@posts.errorhandler(ValidationError)
def validation_error(e):
    return jsonify(e.messages), 400

@posts.errorhandler(Unauthorized)
def unauthorized_error(e):
    return jsonify({'error': e.description}), 401