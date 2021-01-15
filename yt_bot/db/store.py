import logging
from contextlib import contextmanager

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from typing import List, NamedTuple, Union

from yt_bot.db.tables import ProcessedTable
from utils.env import get_env


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
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instances.get(cls):
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    def __init__(self, con_str=None):
        self._engine = self._get_engine(con_str)

    @staticmethod
    def _get_engine(con_str=None):
        if con_str is None:
            host = get_env('HOST')
            port = get_env('PORT')
            db_name = get_env('DB')
            user = get_env('USER')
            password = get_env('PASSWORD')
            con_str = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
        engine = db.create_engine(con_str)
        return engine

    @property
    def engine(self):
        return self._engine


class ProcessedStore(Store):

    def __init__(self, con_str=None) -> None:
        super().__init__(con_str)
        self._session_context = get_session(bind=self._engine)

    def check(self, video_id: str) -> Union[List[ForwardResult], None]:
        with self._session_context() as s:
            results = s.query(ProcessedTable).filter_by(video_id=video_id).all()
            if results:
                forward_results = [ForwardResult(result.chat_id, result.message_id) for result in results]
                return forward_results
            else:
                return None

    def save(self, chat_id, message_id, video_id, link, part) -> None:
        processed = ProcessedTable(chat_id=chat_id, message_id=message_id, video_id=video_id, link=link, part=part)
        with self._session_context() as s:
            s.add(processed)


if __name__ == "__main__":
    pass
