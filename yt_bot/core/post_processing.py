from yt_bot.db.store import Store


def save_processed(msgs):
    db = Store()
    for msg in msgs:
        db.save(msg['link'], msg['chat_id'], msg['message_id'])
