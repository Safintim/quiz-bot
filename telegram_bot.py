import os
import redis
import logging
import telegram
from log_conf import LogsHandler
from dotenv import load_dotenv
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, ConversationHandler, RegexHandler)


logger = logging.getLogger(__name__)

markup = telegram.ReplyKeyboardMarkup([['Новый вопрос', 'Сдаться'], ['Мой счет']])
NEW_QUESTION, SOLUTION_ATTEMPT = range(2)
TAG = 'tg'


def start(bot, update):
    update.message.reply_text('Здравствуйте', reply_markup=markup)
    return NEW_QUESTION


def handle_new_question_request(bot, update):
    question = random.choice(list(answers_for_questions.keys()))
    db.set(update.message.chat_id, question)
    update.message.reply_text(question)
    return SOLUTION_ATTEMPT


def handle_solution_attempt(bot, update):
    question = db.get(update.message.chat_id)

    if update.message.text.lower() == answers_for_questions[question]:
        update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»")
        return NEW_QUESTION
    else:
        update.message.reply_text("Неправильно... Попробуешь ещё раз?")
        return SOLUTION_ATTEMPT


def handle_give_up(bot, update):
    question = db.get(update.message.chat_id)
    update.message.reply_text(f'Правильный ответ: {answers_for_questions[question]}\n'
                              f'Для следующего вопроса нажми "Новый вопрос"')
    return NEW_QUESTION


def handle_cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text(f'Пока {user.first_name}')
    return ConversationHandler.END


def error(bot, update, error):
    logger.exception(f'(quiz-bot) Телеграм Бот упал\nUpdate {update} caused error')


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[LogsHandler()])

    logger.info('(quiz-bot) Телеграм Бот запущен')

    load_dotenv()
    
    global db
    db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True, charset='utf-8')

    updater = Updater(token=os.getenv('TELEGRAM_BOT_TOKEN'))

    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NEW_QUESTION: [RegexHandler('^Новый вопрос$', handle_new_question_request)],
            SOLUTION_ATTEMPT: [RegexHandler('^Сдаться$', handle_give_up),
                               MessageHandler(Filters.text, handle_solution_attempt)],
        },
        fallbacks=[CommandHandler('cancel', handle_cancel)]
    )

    dp.add_handler(conversation_handler)
    dp.add_error_handler(error)
    updater.start_polling()


if __name__ == '__main__':
    main()
