import datetime

from sqlalchemy_utils import JSONType
from pandora.api import db, flask_bcrypt


class Organization(db.Model):
    """ Organization model to store organization details """
    __tablename__ = 'organization'

    id = db.Column(db.Integer(), primary_key=True,
                   autoincrement=True, nullable=False)
    policy = db.Column(JSONType, default={})
    name = db.Column(db.String, nullable=False)
    create_at = db.Column(db.Date, default=datetime.datetime.utcnow())
