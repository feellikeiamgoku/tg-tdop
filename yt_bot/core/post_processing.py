from yt_bot.db.store import ProcessedStore


def save_processed(chat_id, message_id, video_id, link):
    db = ProcessedStore()
    db.save(chat_id, message_id, video_id, link)
