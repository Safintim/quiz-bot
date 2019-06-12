import os
import json
import redis
import random
from read_quiz import get_dicts_questions_answers
from dotenv import load_dotenv

QUIZ = 'quiz'
USERS = 'users'
REPORT = 'report_question'


def format_question_num(num):
    return f'question_{num}'


def format_user_name(tag, user_id):
    return f'user_{tag}_{user_id}'


def load_questions_to_db(db):
    num = 1
    for questions_answers in get_dicts_questions_answers():
        for question, answer in questions_answers.items():
            question_num = format_question_num(num)
            db.hset(QUIZ, question_num,
                    json.dumps({
                        'question': question,
                        'answer': answer
                    }))
            num += 1


def create_report_question(db, user_id, question_key):
    db.hset(REPORT, user_id, question_key)


def create_user(db, tag, user_id, question):
    db.hset(USERS, format_user_name(tag, user_id),
            json.dumps({
                'last_asked_question': question,
                'successful_attempts': 0,
                'failed_attempts': 0,
            }))


def update_user(db, tag, user_id, question, user):
    db.hset(USERS, format_user_name(tag, user_id),
            json.dumps({
                'last_asked_question': question,
                'successful_attempts': user['successful_attempts'],
                'failed_attempts': user['failed_attempts'],
            }))


def update_user_question(db, tag, user_id, question):
    user = get_user(db, tag, user_id)
    if user:
        update_user(db, tag, user_id, question, user)
    else:
        create_user(db, tag, user_id, question)


def update_user_score(db, tag, user_id, user):
    update_user(db, tag, user_id, user['last_asked_question'], user)


def get_random_key_questions(db):
    return format_question_num(random.randint(1, db.hlen(QUIZ)))


def get_question_and_answer(db, key):
    question_answer = json.loads(db.hget(QUIZ, key))
    return question_answer


def get_user(db, tag, user_id):
    user = db.hget(USERS, format_user_name(tag, user_id))
    if user:
        return json.loads(user)


def main():
    load_dotenv()
    db = redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True, charset='utf-8')
    load_questions_to_db(db)


if __name__ == '__main__':
    main()
