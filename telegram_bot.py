import os
import redis
import logging
import telegram
from dotenv import load_dotenv
from read_quiz import get_dict_questions_answers, get_random_question
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, ConversationHandler)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

r = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True, charset='utf-8')

questions_answers = get_dict_questions_answers()

reply_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']
    ]

markup = telegram.ReplyKeyboardMarkup(reply_keyboard)

NEW_QUESTION, SOLUTION_ATTEMPT, GIVE_UP = range(2)


def start(bot, update):
    update.message.reply_text('Здравствуйте', reply_markup=markup)

    return NEW_QUESTION


def handle_new_question_request(bot, update):
    question = get_random_question(questions_answers)
    r.set(update.message.chat_id, question)
    update.message.reply_text(question)

    return SOLUTION_ATTEMPT


def handle_solution_attempt(bot, update):
    question = r.get(update.message.chat_id)

    if update.message.text == questions_answers[question]:
        update.message.reply_text("Правильно! Поздравляю!"
                                  " Для следующего вопроса нажми «Новый вопрос»")
    else:
        update.message.reply_text("Неправильно... Попробуешь ещё раз?")

    return GIVE_UP


def handle_give_up(bot, update):
    question = r.get(update.message.chat_id)
    update.message.reply_text(f'Правильный ответ: {questions_answers[question]}')

    return NEW_QUESTION


def handle_cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text(f'Пока {user.first_name}')
    return ConversationHandler.END


def error(bot, update, error):
    logger.exception(f'(quiz-bot) Телеграм Бот упал\nUpdate {update} caused error')


def main():
    load_dotenv()
    logger.info('(quiz-bot) Телеграм Бот запущен')
    updater = Updater(token=os.getenv('TELEGRAM_BOT'), request_kwargs={
        'proxy_url': 'http://51.38.80.159:80/'
    })

    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            NEW_QUESTION: [],

            SOLUTION_ATTEMPT: [],

            GIVE_UP: []
        },

        fallbacks=[]
    )

    dp.add_handler(conversation_handler)
    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()


if __name__ == '__main__':
    main()
