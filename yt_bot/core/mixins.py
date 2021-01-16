from abc import ABC


class TelegramMixin(ABC):

    def notify(self, msg):
        msg = self._bot.send_message(chat_id=self._chat_id, text=msg)
        return msg

    def send_audio(self, filepath: str, timeout=1000):
        msg = self._bot.send_audio(self._chat_id, open(filepath, 'rb'), timeout=timeout)
        return msg

    def forward(self, from_chat_id, message_id, to_chat=None):
        to_chat = to_chat if to_chat else self._chat_id
        msg = self._bot.forward_message(to_chat, from_chat_id, message_id)
        return msg
