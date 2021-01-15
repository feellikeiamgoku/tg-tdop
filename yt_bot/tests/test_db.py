import pytest
from unittest import mock

from yt_bot.db.store import get_session, ProcessedStore, ForwardResult
from yt_bot.db.initialize import Initializer
from yt_bot.db.tables import ProcessedTable


@pytest.fixture
def table():
    return ProcessedTable


@pytest.fixture
def fake_table():
    class SomeTable:
        pass

    return SomeTable


class TestInitialize:

    @mock.patch('yt_bot.db.initialize.ProcessedStore._get_engine')
    def test_register(self, engine, table):
        initializer = Initializer()
        initializer.register(table)
        assert table in initializer._registered

        with pytest.raises(TypeError):
            initializer.register('table')

    @mock.patch('yt_bot.db.initialize.ProcessedStore._get_engine')
    def test_run(self, engine, table, fake_table):
        initializer = Initializer()
        initializer._registered.append(table)
        initializer.run()

        initializer._registered.append(fake_table)
        with pytest.raises(TypeError):
            initializer.run()


class TestProcessedStore:

    @mock.patch('yt_bot.db.initialize.ProcessedStore._get_engine')
    def test_singleton(self, engine):
        store = ProcessedStore()

        store2 = ProcessedStore()
        assert store is store2

    @mock.patch('yt_bot.db.store.db.create_engine')
    def test_get_engine(self, engine):
        with pytest.raises(KeyError):
            store = ProcessedStore()

    def test_same_engine(self):
        pr_store = ProcessedStore('sqlite://')

        pr_store2 = ProcessedStore('sqlite://')

        assert pr_store.engine is pr_store2.engine


def test_session_context():
    pass


pytest.main()
