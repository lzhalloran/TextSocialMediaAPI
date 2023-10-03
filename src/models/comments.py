from main import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)
    created_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    user = db.relationship(
        "User",
        back_populates="comments"
    )
    post = db.relationship(
        "Post",
        back_populates="comments"
    )