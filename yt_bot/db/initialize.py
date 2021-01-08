import inspect
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from yt_bot.db.store import Store

_Base = declarative_base()


class Initializer:
    class Processed(_Base):
        __tablename__ = 'processed'
        id = db.Column(db.Integer, autoincrement=True, primary_key=True)
        video_id = db.Column(db.VARCHAR(100))
        link = db.Column(db.VARCHAR(150))
        chat_id = db.Column(db.Integer)
        message_id = db.Column(db.Integer)
        part = db.Column(db.Integer, default=db.null)

    @classmethod
    def run(cls):
        engine = Store.get_engine()

        for name, attr in vars(cls).items():
            if inspect.isclass(attr):
                attr.__table__.create(bind=engine, checkfirst=True)


if __name__ == "__main__":
    Initializer.run()
