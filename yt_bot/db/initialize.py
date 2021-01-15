from yt_bot.db.processedstore import Store
from yt_bot.db.tables import _Base


class Initializer:

    def __init__(self):
        self._store = Store()
        self._registered = []

    def register(self, table_class):
        if issubclass(table_class, _Base):
            self._registered.append(table_class)
            return table_class
        raise TypeError("Can only register tables from instances of 'declarative base'")

    def run(self):
        engine = self._store.get_engine()
        for table in self._registered:
            if issubclass(table, _Base):
                table.__table__.create(bind=engine, checkfirst=True)
            else:
                raise TypeError("Can only create tables from instances of 'declarative base'")

