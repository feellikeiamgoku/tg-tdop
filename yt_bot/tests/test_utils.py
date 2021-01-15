import os


from utils.context import DirContext


class TestContext:
    def test_message_path(self):
        dc = DirContext(123, 28)
        path = dc.get_message_path()
        assert path == os.path.join(os.getcwd(), '123', '28')

    def test_context(self):
        base_dir = os.getcwd()
        with DirContext(123, 28) as path:
            assert path == os.getcwd()
        assert base_dir == os.getcwd()

