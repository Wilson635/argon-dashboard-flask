from apps import db


class Members(db.Model):
    __tablename__ = 'Members'

    idMember = db.Column(db.Interger, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    familySituation = db.Column(db.String(64), unique=True, nullable=False)
    occupation = db.Column(db.String(64), unique=True, nullable=False)
