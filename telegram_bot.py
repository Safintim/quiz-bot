import os
import telegram
from redis_db import db
from logger_bot import logger
from read_quiz import get_dict_questions_answers, get_random_question
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, ConversationHandler, RegexHandler)


questions_answers = get_dict_questions_answers()
markup = telegram.ReplyKeyboardMarkup([['Новый вопрос', 'Сдаться'], ['Мой счет']])

NEW_QUESTION, SOLUTION_ATTEMPT = range(2)


def start(bot, update):
    update.message.reply_text('Здравствуйте', reply_markup=markup)
    return NEW_QUESTION


def handle_new_question_request(bot, update):
    question = get_random_question(questions_answers)
    db.set(update.message.chat_id, question)
    update.message.reply_text(question)
    return SOLUTION_ATTEMPT


def handle_solution_attempt(bot, update):
    question = db.get(update.message.chat_id)

    if update.message.text.lower() == questions_answers[question]:
        update.message.reply_text("Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»")
        return NEW_QUESTION
    else:
        update.message.reply_text("Неправильно... Попробуешь ещё раз?")
        return SOLUTION_ATTEMPT


def handle_give_up(bot, update):
    question = db.get(update.message.chat_id)
    update.message.reply_text(f'Правильный ответ: {questions_answers[question]}\n'
                              f'Для следующего вопроса нажми "Новый вопрос"')
    return NEW_QUESTION


def handle_cancel(bot, update):
    user = update.message.from_user
    update.message.reply_text(f'Пока {user.first_name}')
    return ConversationHandler.END


def error(bot, update, error):
    logger.exception(f'(quiz-bot) Телеграм Бот упал\nUpdate {update} caused error')


def main():
    logger.info('(quiz-bot) Телеграм Бот запущен')
    updater = Updater(token=os.getenv('TELEGRAM_BOT'))

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
