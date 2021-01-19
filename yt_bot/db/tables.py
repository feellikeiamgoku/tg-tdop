import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()


class ProcessedTable(_Base):
    __tablename__ = 'processed'
    video_id = db.Column(db.VARCHAR(100), primary_key=True)
    link = db.Column(db.VARCHAR(150))
    chat_id = db.Column(db.Integer)
    message_id = db.Column(db.Integer)
