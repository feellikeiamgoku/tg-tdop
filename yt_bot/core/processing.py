from yt_bot.yt.fetch import download
from yt_bot.yt.context import DirContext


def _process(chat_id, message_id, bot, audio):
    with DirContext(chat_id, message_id):
        download(audio.link)

        msg = bot.send_audio(chat_id, open(audio.get_path(), 'rb'), performer=audio.author, title=audio.title)

        audio.set_postprocess_values(chat_id, msg.message_id)
        return audio


def process(chat_id, message_id, bot, *descriptions):
    msgs = [_process(chat_id, message_id, bot, audio) for audio in descriptions]
    return msgs
