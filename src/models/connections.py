from main import db
from datetime import date

class Connection(db.Model):
    __tablename__ = "connections"
    id = db.Column(db.Integer, primary_key=True)
    requested_date = db.Column(db.Date(), default=date.today(), nullable=False)
    accepted_date = db.Column(db.Date(), default=None, nullable=True)
    requestor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    acceptor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    requestor = db.relationship(
        "User",
        back_populates="connections_requestor",
        foreign_keys=[requestor_id]
    )
    acceptor = db.relationship(
        "User",
        back_populates="connections_acceptor",
        foreign_keys=[acceptor_id]
    )
    