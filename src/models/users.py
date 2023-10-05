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
    comments = db.relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete"
    )
    connections_requestor = db.relationship(
        "Connection",
        back_populates="requestor",
        foreign_keys='Connection.requestor_id',
        cascade="all, delete"
    )
    connections_acceptor = db.relationship(
        "Connection",
        back_populates="acceptor",
        foreign_keys='Connection.acceptor_id',
        cascade="all, delete"
    )
    memberships = db.relationship(
        "Membership",
        back_populates="user",
        cascade="all, delete"
    )