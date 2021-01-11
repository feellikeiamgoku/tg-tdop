from yt_bot.db.store import Store


def save_processed(chat_id, message_id, video_id, link):
    db = Store()
    db.save(chat_id, message_id, video_id, link)
