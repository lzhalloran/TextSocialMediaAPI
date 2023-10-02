from main import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(254), nullable=False)
    password = db.Column(db.String(), nullable=False)
    bio = db.Column(db.String(200))
    posts = db.relationship(
        "Post",
        back_populates="user",
        cascade="all, delete"
    )