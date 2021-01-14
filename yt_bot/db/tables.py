import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base


_Base = declarative_base()


class ProcessedTable(_Base):
    __tablename__ = 'processed'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    video_id = db.Column(db.VARCHAR(100))
    link = db.Column(db.VARCHAR(150))
    chat_id = db.Column(db.Integer)
    message_id = db.Column(db.Integer)
    part = db.Column(db.Integer, default=db.null)
