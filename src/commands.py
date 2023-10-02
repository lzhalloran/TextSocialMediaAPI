from main import db
from flask import Blueprint
from main import bcrypt
from models.users import User
from models.posts import Post

db_commands = Blueprint("db", __name__)


@db_commands .cli.command("create")
def create_db():
    print("Creating Tables...")
    db.create_all()
    print("Created Tables.")


@db_commands .cli.command("seed")
def seed_db():
    print("Seeding Tables...")
    post1 = Post(
        text = "Hi, this is the first post!"
    )
    db.session.add(post1)

    post2 = Post(
        text = "Second post here"
    )
    db.session.add(post2)

    
    user1 = User(
        username = "user1",
        email = "user1@email.com",
        password = bcrypt.generate_password_hash("user1password").decode("utf-8"),
        bio = "Hi, I'm user one, and this is my bio, check out my posts!"
    )
    db.session.add(user1)

    user2 = User(
        username = "user2",
        email = "user2@email.com",
        password = bcrypt.generate_password_hash("user2password").decode("utf-8"),
        bio = "Second user here, feel free to connect!"
    )
    db.session.add(user2)

    db.session.commit()
    print("Seeded Tables.")


@db_commands .cli.command("drop")
def drop_db():
    print("Dropping Tables...")
    db.drop_all()
    print("Dropped Tables.")