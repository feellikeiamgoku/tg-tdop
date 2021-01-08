import os

import sqlalchemy as db
from yt_bot.validation.definition import Audio


class Store:
    def __init__(self):
        self._engine = self.get_engine()
        self.con = self._engine.connect()
        self._metadata = db.MetaData()
        self._table_name = 'processed'

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

    def check(self, entity: Audio):
        table = db.Table(self._table_name, self._metadata, autoload=True, autoload_with=self._engine)

        query = db.select([table]).where(table.c.video_id == entity.video_id)

        result = self.con.execute(query).fetchone()

        return result

    def save(self, audio: Audio):
        table = db.Table(self._table_name, self._metadata, autoload=True, autoload_with=self._engine)

        query = db.insert(table).values(video_id=audio.video_id, chat_id=audio.chat_id, message_id=audio.message_id,
                                        link=audio.link)

        self.con.execute(query)


if __name__ == "__main__":
    pass
