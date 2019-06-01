import os
import redis
import logging
import telegram
from dotenv import load_dotenv
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from read_quiz import get_dict_questions_answers, get_random_question


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

NEW_QUESTION, SOLUTION_ATTEMPT = range(2)


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

    return


def echo(bot, update):
    question_answer = get_random_question(questions_answers)
    question = question_answer[0]
    answer = question_answer[1]

    if update.message.text == 'Новый вопрос':
        print(question)
        print(answer)
        update.message.reply_text(question)
        r.set(update.message.chat_id, question)
    elif update.message.text == 'Сдаться':
        ...
        # print(answer)
        # update.message.reply_text(answer)
        # print(r.get(update.message.chat_id))
        # update.message.reply_text()
    else:
        current_question = r.get(update.message.chat_id)
        if update.message.text == questions_answers[current_question]:
            update.message.reply_text("Правильно! Поздравляю!"
                                      " Для следующего вопроса нажми «Новый вопрос»")
        else:
            update.message.reply_text("Неправильно... Попробуешь ещё раз?")


def error(bot, update, error):
    logger.exception(f'(smart-bots) Телеграм Бот упал\nUpdate {update} caused error')


def main():
    load_dotenv()
    logger.info('(smart-bots) Телеграм Бот запущен')
    updater = Updater(token=os.getenv('TELEGRAM_BOT'), request_kwargs={
        'proxy_url': 'http://151.106.8.237:8080/'
    })

    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={},

        fallbacks=[]
    )

    dp.add_handler(conversation_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()


if __name__ == '__main__':
    main()
