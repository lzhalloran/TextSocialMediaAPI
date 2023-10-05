from main import db
from datetime import datetime

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)
    created_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), default=None, nullable=True)
    user = db.relationship(
        "User",
        back_populates="posts"
    )    
    comments = db.relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete"
    )
    group = db.relationship(
        "Group",
        back_populates="posts"
    )