from yt_bot.db.store import ProcessedStore


class PostDownload:
    def __init__(self):
        self._db = ProcessedStore()

    def post_save(self, chat_id, message_id, video_id, link, part=1):
        self._db.save(chat_id, message_id, video_id, link, part=part)
