import os
import logging
import telegram
from functools import partial


def create_bot_logger(token):
    bot = telegram.Bot(token)
    return bot


def send_report(bot, chat_id, msg):
    bot.send_message(chat_id=chat_id, text=msg)


send_report = partial(send_report,
                      create_bot_logger(os.getenv('LOGGER_BOT_TOKEN')),
                      os.getenv('LOGS_RECEIVER_ID'))


def create_logger(logs_handler):
    logger = logging.getLogger('Bot Logger')
    handler = logs_handler
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


class LogsHandler(logging.Handler):

    def __init__(self):
        super().__init__()

    def emit(self, record):
        log_entry = self.format(record)
        send_report(log_entry)


logger = create_logger(LogsHandler())
