from main import db
from flask import Blueprint
from main import bcrypt
from models.users import User
from models.posts import Post
from models.comments import Comment
from models.connections import Connection
from models.groups import Group
from models.memberships import Membership

db_commands = Blueprint("db", __name__)


@db_commands .cli.command("create")
def create_db():
    print("Creating Tables...")
    db.create_all()
    print("Created Tables.")


@db_commands .cli.command("seed")
def seed_db():
    print("Seeding Tables...")
    
    # Seed some Users in the database
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

    # Seed some Groups in the database
    group1 = Group(
        name = "Group 1",
        bio = "This is the page for Group 1!"
    )
    db.session.add(group1)

    group2 = Group(
        name = "Group 2"
    )
    db.session.add(group2)

    db.session.commit()

    # Seed some Memberships in the database
    membership1 = Membership(
        user = user1,
        group = group1,
        admin = True
    )
    db.session.add(membership1)

    membership2 = Membership(
        user = user2,
        group = group1
    )
    db.session.add(membership2)

    membership3 = Membership(
        user = user2,
        group = group2
    )
    db.session.add(membership3)

    db.session.commit()

    # Seed some Posts in the database
    post1 = Post(
        text = "Hi, this is the first post!",
        user_id = user1.id
    )
    db.session.add(post1)

    post2 = Post(
        text = "Second post here", 
        user = user2
    )
    db.session.add(post2)

    post3 = Post(
        text = "The first post in Group 1!",
        user = user1,
        group = group1
    )
    db.session.add(post3)

    post4 = Post(
        text = "Group 2's first post!",
        user = user2,
        group = group2
    )
    db.session.add(post4)

    db.session.commit()

    # Seed some Comments in the database
    comment1 = Comment(
        text = "Congratulations on your first post, user 1!",
        user = user2,
        post = post1
    )
    db.session.add(comment1)

    comment2 = Comment(
        text = "Nice post user 2!",
        user = user1,
        post = post2
    )
    db.session.add(comment2)

    comment3 = Comment(
        text = "Commenting on a post in group 1",
        user = user1,
        post = post3
    )
    db.session.add(comment3)

    comment4 = Comment(
        text = "Nice group post comment, user 1!",
        user = user2,
        post = post3
    )
    db.session.add(comment4)

    db.session.commit()

    # Seed some Connections in the database
    connection1 = Connection(
        requestor = user1,
        acceptor = user2
    )
    db.session.add(connection1)

    db.session.commit()

    print("Seeded Tables.")


@db_commands .cli.command("drop")
def drop_db():
    print("Dropping Tables...")
    db.drop_all()
    print("Dropped Tables.")