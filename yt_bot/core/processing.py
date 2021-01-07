from yt_bot.yt.fetch import download
from yt_bot.yt.context import DirContext


def _process(chat_id, message_id, bot, link):
    with DirContext(chat_id, message_id):
        audio = download(link)

        msg = bot.send_audio(chat_id, open(audio.path, 'rb'), performer=audio.author, title=audio.filename)

        return {"message_id": msg.message_id, "link": link, "chat_id": chat_id}


def process(chat_id, message_id, bot, *descriptions):
    msgs = [_process(chat_id, message_id, bot, descr.link) for descr in descriptions]
    return msgs
