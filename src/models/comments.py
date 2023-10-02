from main import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)
    created_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)