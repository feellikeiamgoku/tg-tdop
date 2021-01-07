import os
import pathlib
import shutil

from threading import Lock

DirLock = Lock()


class DirContext:

    def __init__(self, chat_id, message_id):
        self.chat_id = str(chat_id)
        self.message_id = str(message_id)
        self.base_path = os.getcwd()

    def __enter__(self):
        path = self.get_message_path()
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        os.chdir(path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        path = self.get_message_path()
        shutil.rmtree(path)
        os.chdir(self.base_path)

    def get_message_path(self):
        return os.path.join(self.base_path, self.chat_id, self.message_id)
