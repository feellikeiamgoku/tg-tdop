from yt_bot.db.store import Store


def save_processed(audio):
    db = Store()
    db.save(audio)
