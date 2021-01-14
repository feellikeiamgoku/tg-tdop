from yt_bot.db.store import Store


class Initializer:
    _registered = []

    @classmethod
    def register(cls, table_class):
        cls._registered.append(table_class)
        return table_class

    @classmethod
    def run(cls):
        engine = Store.get_engine()
        for table in cls._registered:
            table.__table__.create(bind=engine, checkfirst=True)
