import os
import redis
import vk_api
from dotenv import load_dotenv
from logger_bot import logger
from read_quiz import get_dict_questions_answers, get_random_question
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


load_dotenv()

questions_answers = get_dict_questions_answers()

db = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True, charset='utf-8')


def handle_new_question_request(event, api):
    question = get_random_question(questions_answers)
    print(question)
    print(questions_answers[question])
    db.set(event.user_id, question)
    api.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message=question
    )


def handle_solution_attempt(event, api):
    question = db.get(event.user_id)

    if event.text.lower() == questions_answers[question]:
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
        message=f'Правильный ответ: {questions_answers[question]}\nДля следующего вопроса нажми "Новый вопрос"'
    )


def start_bot():
    vk_session = vk_api.VkApi(token=os.getenv('VK_BOT'))
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
    while True:
        try:
            logger.info('(quiz-bot) ВК Бот запущен')
            start_bot()
        except vk_api.VkApiError:
            logger.exception('(quiz-bot) ВК Бот упал')


if __name__ == "__main__":
    main()
