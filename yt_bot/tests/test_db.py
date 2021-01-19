from types import FunctionType
from unittest import mock

import pytest

from yt_bot.db.initialize import Initializer
from yt_bot.db.store import ProcessedStore, ForwardResult, Store, get_session
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

    @mock.patch('yt_bot.db.initialize.Store._get_engine')
    def test_register(self, engine, table):
        initializer = Initializer()
        initializer.register(table)
        assert table in initializer._registered

        with pytest.raises(TypeError):
            initializer.register('table')

    @mock.patch('yt_bot.db.initialize.Store._get_engine')
    def test_run(self, engine, table, fake_table):
        initializer = Initializer()
        initializer._registered.append(table)
        initializer.run()

        initializer._registered.append(fake_table)
        with pytest.raises(TypeError):
            initializer.run()


class TestStore:
    @mock.patch('yt_bot.db.initialize.Store._get_engine')
    def test_singleton(self, engine):
        store = Store()

        store2 = Store()
        assert store is store2

    @mock.patch('yt_bot.db.store.db.create_engine')
    def test_get_engine(self, engine):
        with pytest.raises(KeyError):
            store = Store()

    def test_same_engine(self):
        store = Store('sqlite://')

        store2 = Store('sqlite://')

        assert store.engine is store2.engine


class TestProcessedStore:

    @pytest.fixture
    def setup_db(self):
        pr_store = ProcessedStore('sqlite://')

        ProcessedTable.__table__.create(bind=pr_store.engine, checkfirst=True)
        pr_store.engine.execute('''
        insert into processed (video_id, link, chat_id, message_id) 
        values('test', 'link', 1, 2),
               ('test1', 'link', 1, 3),
               ('another_test', 'link', 2, 8)
               ''')
        return pr_store

    def test_check(self, setup_db: ProcessedStore):
        store = setup_db
        value = store.check('xyz')
        assert value is None

        value = store.check('another_test')
        assert isinstance(value, ForwardResult)
        assert value.chat_id == 2
        assert value.message_id == 8

    def test_save(self, setup_db: ProcessedStore):
        store = setup_db
        store.save(1, 2, 'from_test_save', 'link')
        value = store.engine.execute('''
        select * from processed where video_id = 'from_test_save'
        ''').fetchall()
        assert value[0][0] == 'from_test_save'


@mock.patch('yt_bot.db.store.sessionmaker')
def test_session_context(sessionmaker):
    session_func = get_session()
    assert sessionmaker.called
    assert isinstance(session_func, FunctionType)


pytest.main()
