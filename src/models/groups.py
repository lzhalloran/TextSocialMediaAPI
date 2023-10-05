from main import db

class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    bio = db.Column(db.String(200))
    posts = db.relationship(
        "Post",
        back_populates="group",
        cascade="all, delete"
    )