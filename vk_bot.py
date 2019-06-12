import os
import redis
import vk_api
import logging
import requests
import db_tools
from log_conf import LogsHandler
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

logger = logging.getLogger(__name__)

TAG = 'vk'


def handle_new_question_request(event, api):
    question_key = db_tools.get_random_key_questions(db_redis)
    question_and_answer = db_tools.get_question_and_answer(db_redis, question_key)
    db_tools.update_user_question(db_redis, TAG, event.obj.peer_id, question_key)
    api.messages.send(
        peer_id=event.obj.peer_id,
        random_id=get_random_id(),
        message=question_and_answer['question']
    )


def handle_solution_attempt(event, api):
    user = db_tools.get_user(db_redis, TAG, event.obj.peer_id)
    question_key = user['last_asked_question']
    question_and_answer = db_tools.get_question_and_answer(db_redis, question_key)
    if event.obj.text.lower().strip() == question_and_answer['answer']:
        user['successful_attempts'] += 1
        db_tools.update_user_score(db_redis, TAG, event.obj.peer_id, user)

        api.messages.send(
            peer_id=event.obj.peer_id,
            random_id=get_random_id(),
            message="Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        )
    else:
        user['failed_attempts'] += 1
        db_tools.update_user_score(db_redis, TAG, event.obj.peer_id, user)

        api.messages.send(
            peer_id=event.obj.peer_id,
            random_id=get_random_id(),
            message="Неправильно... Попробуешь ещё раз?"
        )


def handle_give_up(event, api):
    user = db_tools.get_user(db_redis, TAG, event.obj.peer_id)
    question_key = user['last_asked_question']
    question_and_answer = db_tools.get_question_and_answer(db_redis, question_key)
    api.messages.send(
        peer_id=event.obj.peer_id,
        random_id=get_random_id(),
        message=f'Правильный ответ: {question_and_answer["answer"]}\nДля следующего вопроса нажми "Новый вопрос"'
    )


def handle_report_question(event, api):
    user = db_tools.get_user(db_redis, TAG, event.obj.peer_id)
    db_tools.create_report_question(db_redis, event.user_id, user['last_asked_question'])

    api.messages.send(
        peer_id=event.obj.peer_id,
        random_id=get_random_id(),
        message='Разберемся\nДля следующего вопроса нажми "Новый вопрос"'
    )


def handle_my_score(event, api):
    user = db_tools.get_user(db_redis, TAG, event.obj.peer_id)

    api.messages.send(
        peer_id=event.obj.peer_id,
        random_id=get_random_id(),
        message=f'Количество удачных попыток: {user["successful_attempts"]}\n'
                f'Количество неудачный попыток: {user["failed_attempts"]}'
    )


def start_bot():

    load_dotenv()
    global db_redis
    db_redis = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True, charset='utf-8')

    vk_session = vk_api.VkApi(token=os.getenv('VK_BOT_TOKEN'))
    vk = vk_session.get_api()

    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Пожаловаться на вопрос', color=VkKeyboardColor.POSITIVE)
    while True:
        longpoll = VkBotLongPoll(vk_session, os.getenv('VK_GROUP_ID'))
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.obj.text == 'Новый вопрос':
                        handle_new_question_request(event, vk)
                    elif event.obj.text == 'Сдаться':
                        handle_give_up(event, vk)
                    elif event.obj.text == 'Мой счет':
                        handle_my_score(event, vk)
                    elif event.obj.text == 'Неверно составленный вопрос':
                        handle_report_question(event, vk)
                    else:
                        handle_solution_attempt(event, vk)
        except requests.exceptions.ReadTimeout:
            continue


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[LogsHandler()])

    while True:
        try:
            logger.info('(quiz-bot) ВК Бот запущен')
            start_bot()
        except vk_api.VkApiError:
            logger.exception('(quiz-bot) ВК Бот упал')


if __name__ == "__main__":
    main()
