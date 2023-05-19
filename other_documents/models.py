import datetime

from app import db


class OtherDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225), nullable=False)
    file_path = db.Column(db.String(225), nullable=False)
    date_download = db.Column(db.Date, default=datetime.date.today())
    comment = db.Column(db.String(225))

    def __repr__(self):
        return self.name
