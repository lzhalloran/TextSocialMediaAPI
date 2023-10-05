from main import db
from datetime import date

class Membership(db.Model):
    __tablename__ = "memberships"
    id = db.Column(db.Integer, primary_key=True)
    requested_date = db.Column(db.Date(), default=date.today(), nullable=False)
    accepted_date = db.Column(db.Date(), default=None, nullable=True)
    admin = db.Column(db.Boolean, default = False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    user = db.relationship(
        "User",
        back_populates="memberships",
        foreign_keys=[user_id]
    )
    group = db.relationship(
        "Group",
        back_populates="memberships",
        foreign_keys=[group_id]
    )
