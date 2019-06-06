import os
import logging
import telegram


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
        self.bot = telegram.Bot(os.getenv('LOGGER_BOT_TOKEN'))

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=os.getenv('LOGS_RECEIVER_ID'), text=log_entry)


logger = create_logger(LogsHandler())
