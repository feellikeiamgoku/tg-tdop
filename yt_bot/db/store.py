import os

from sqlalchemy import create_engine, MetaData, Table, select

from yt_bot.validation.definition import YTWatch


class Store:
    def __init__(self):
        self._engine = self.get_engine()
        self.con = self._engine.connect()
        self._metadata = MetaData()
        self._table_name = 'processed'

    def get_engine(self):
        host = os.getenv('HOST')
        port = os.getenv('PORT')
        db = os.getenv('DB')
        user = os.getenv('USER')
        password = os.getenv('PASSWORD')
        con_str = f'postgresql://{user}:{password}@{host}:{port}/{db}'
        engine = create_engine(con_str)
        return engine

    def check(self, entity: YTWatch):
        table = Table(self._table_name, self._metadata, autoload=True, autoload_with=self._engine)

        query = select([table]).where(table.c.link == entity.link)

        result = self.con.execute(query).fetchone()

        return result

    def store(self, entity: YTWatch):
        pass


if __name__ == "__main__":
    store = Store()
    res = store.check('https://www.youtube.com/watch?v=J43eZqsTBEc&list=PL7T6cfreEgTCW8nIEOjg1XsgQ5zf086u4&index=1')
