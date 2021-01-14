import os
import logging
from contextlib import contextmanager

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from typing import List, NamedTuple

from yt_bot.db.tables import ProcessedTable


def get_session(*args, **kwargs):
    session_cls = sessionmaker(*args, **kwargs)

    @contextmanager
    def inner():
        session = session_cls()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(e)
            raise
        finally:
            session.close()

    return inner


class ForwardResult(NamedTuple):
    chat_id: str
    message_id: str


class Store:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._engine = self.get_engine()
        self._session_context = get_session(bind=self._engine)

    @staticmethod
    def get_engine():
        host = os.getenv('HOST')
        port = os.getenv('PORT')
        db_name = os.getenv('DB')
        user = os.getenv('USER')
        password = os.getenv('PASSWORD')
        con_str = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
        engine = db.create_engine(con_str)
        return engine

    def check(self, video_id: str) -> List[ForwardResult]:
        with self._session_context() as s:
            results = s.query(ProcessedTable).filter_by(video_id=video_id).all()
            if results:
                forward_results = [ForwardResult(result.chat_id, result.message_id) for result in results]
                return forward_results
            else:
                return None

    def save(self, chat_id, message_id, video_id, link, part):
        processed = ProcessedTable(chat_id=chat_id, message_id=message_id, video_id=video_id, link=link, part=part)
        with self._session_context() as s:
            s.add(processed)


if __name__ == "__main__":
    db = Store()
    db.check('dexiQGxBNFw')
