import os
import redis
import random
import vk_api
import logging
from log_conf import LogsHandler
from dotenv import load_dotenv
from read_quiz import get_dict_questions_answers
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


logger = logging.getLogger(__name__)

answers_for_questions = get_dict_questions_answers()


def handle_new_question_request(event, api):
    question = random.choice(list(answers_for_questions.keys()))
    db.set(event.user_id, question)
    api.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message=question
    )


def handle_solution_attempt(event, api):
    question = db.get(event.user_id)

    if event.text.lower() == answers_for_questions[question]:
        api.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            message="Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»"
        )
    else:
        api.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            message="Неправильно... Попробуешь ещё раз?"
        )


def handle_give_up(event, api):
    question = db.get(event.user_id)
    api.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message=f'Правильный ответ: {answers_for_questions[question]}\n'
                f'Для следующего вопроса нажми "Новый вопрос"'
    )


def start_bot():

    load_dotenv()
    global db
    db = redis.Redis(
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

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                handle_new_question_request(event, vk)
            elif event.text == 'Сдаться':
                handle_give_up(event, vk)
            else:
                handle_solution_attempt(event, vk)


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
