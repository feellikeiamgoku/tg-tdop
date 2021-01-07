from yt_bot.db.store import Store


def save_processed(msgs):
    db = Store()
    for audio in msgs:
        db.save(audio)
