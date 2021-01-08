import os

from sqlalchemy import create_engine, MetaData, Table, select, insert

from yt_bot.validation.definition import Audio


class Store:
    def __init__(self):
        self._engine = self.get_engine()
        self.con = self._engine.connect()
        self._metadata = MetaData()
        self._table_name = 'processed'

    def get_engine(self):
        con_str = os.getenv('DATABASE_URL')
        engine = create_engine(con_str)
        return engine

    def check(self, entity: Audio):
        table = Table(self._table_name, self._metadata, autoload=True, autoload_with=self._engine)

        query = select([table]).where(table.c.video_id == entity.video_id)

        result = self.con.execute(query).fetchone()

        return result

    def save(self, audio:Audio):
        table = Table(self._table_name, self._metadata, autoload=True, autoload_with=self._engine)

        query = insert(table).values(video_id=audio.video_id, chat_id=audio.chat_id, message_id=audio.message_id,
                                     link=audio.link)

        self.con.execute(query)


if __name__ == "__main__":
    pass
