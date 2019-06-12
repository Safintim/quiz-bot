import os
import db_tools
import redis
import logging
import telegram
from log_conf import LogsHandler
from dotenv import load_dotenv
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, ConversationHandler, RegexHandler)


logger = logging.getLogger(__name__)

markup = telegram.ReplyKeyboardMarkup([['Новый вопрос', 'Сдаться'], ['Мой счет', 'Пожаловаться на вопрос']])
NEW_QUESTION, SOLUTION_ATTEMPT = range(2)
TAG = 'tg'


def start(bot, update):
    update.message.reply_text('Здравствуйте', reply_markup=markup)
    return NEW_QUESTION


def handle_new_question_request(bot, update):
    question_key = db_tools.get_random_key_questions(db_redis)
    question_and_answer = db_tools.get_question_and_answer(db_redis, question_key)

    db_tools.update_user_question(db_redis, TAG, update.message.chat_id, question_key)

    update.message.reply_text(question_and_answer['question'])
    return SOLUTION_ATTEMPT


def handle_solution_attempt(bot, update):
    user = db_tools.get_user(db_redis, TAG, update.message.chat_id)
    question_key = user['last_asked_question']
    question_and_answer = db_tools.get_question_and_answer(db_redis, question_key)

    if update.message.text.lower().strip() == question_and_answer['answer']:
        update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»")
        user['successful_attempts'] += 1
        db_tools.update_user_score(db_redis, TAG, update.message.chat_id, user)
        return NEW_QUESTION
    else:
        user['failed_attempts'] += 1
        db_tools.update_user_score(db_redis, TAG, update.message.chat_id, user)
        update.message.reply_text("Неправильно... Попробуешь ещё раз?")
        return SOLUTION_ATTEMPT


def handle_give_up(bot, update):
    user = db_tools.get_user(db_redis, TAG, update.message.chat_id)
    question_key = user['last_asked_question']
    question_and_answer = db_tools.get_question_and_answer(db_redis, question_key)
    update.message.reply_text(f'Правильный ответ: {question_and_answer["answer"]}\n'
                              f'Для следующего вопроса нажми "Новый вопрос"')
    return NEW_QUESTION


def handle_report_question(bot, update):
    user = db_tools.get_user(db_redis, TAG, update.message.chat_id)
    db_tools.create_report_question(db_redis, update.message.chat_id, user['last_asked_question'])
    update.message.reply_text('Разберемся\nДля следующего вопроса нажми "Новый вопрос"')
    return NEW_QUESTION


def handle_my_score(bot, update):
    user = db_tools.get_user(db_redis, 'tg', update.message.chat_id)
    update.message.reply_text(f'Количество удачных попыток: {user["successful_attempts"]}\n'
                              f'Количество неудачный попыток: {user["failed_attempts"]}')


def handle_cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text(f'Пока {user.first_name}')
    return ConversationHandler.END


def error(bot, update, error):
    logger.exception(f'(quiz-bot) Телеграм Бот упал\nUpdate {update} caused error\n {error}')


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[LogsHandler()])

    logger.info('(quiz-bot) Телеграм Бот запущен')

    load_dotenv()
    
    global db_redis
    db_redis = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True, charset='utf-8')

    updater = Updater(token=os.getenv('TELEGRAM_BOT_TOKEN'))

    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NEW_QUESTION: [RegexHandler('^Новый вопрос$', handle_new_question_request),
                           RegexHandler('^Пожаловаться на вопрос$', handle_report_question)],
            SOLUTION_ATTEMPT: [RegexHandler('^Сдаться$', handle_give_up),
                               RegexHandler('^Неверно составленный вопрос$', handle_report_question),
                               MessageHandler(Filters.text, handle_solution_attempt)],
        },
        fallbacks=[CommandHandler('cancel', handle_cancel)]
    )
    dp.add_handler(RegexHandler('^Мой счет$', handle_my_score))
    dp.add_handler(conversation_handler)
    dp.add_error_handler(error)
    updater.start_polling()


if __name__ == '__main__':
    main()
