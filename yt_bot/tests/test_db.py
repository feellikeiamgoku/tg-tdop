import pytest
from unittest import mock

from yt_bot.db.processedstore import get_session, ProcessedStore, ForwardResult
from yt_bot.db.initialize import Initializer
from yt_bot.db.tables import ProcessedTable


@pytest.fixture
def table():
    return ProcessedTable


class TestInitialize:

    def test_register(self, table):
        initializer = Initializer()
        initializer.register(table)
        assert table in initializer._registered

        with pytest.raises(TypeError):
            initializer.register('table')

    @mock.patch('yt_bot.db.initialize.Store.get_engine')
    def test_run(self, engine, table):
        initializer = Initializer()
        initializer._registered.append(table)
        initializer.run()

        class SomeTable:
            pass

        initializer._registered.append(SomeTable)
        with pytest.raises(TypeError):
            initializer.run()


class TestStore:
    pass


def test_session_context():
    pass


pytest.main()
