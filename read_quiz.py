import random
import os
import os.path
from format_answer import form_answer


def get_random_file(directory='quiz-questions'):
    file = random.choice([file for file in os.listdir(directory) if file.endswith('.txt')])
    return os.path.join(directory, file)


def read_file(file):
    with open(file, 'r', encoding='KOI8-R') as f:
        return f.read()


def form_dict_questions_answers(text):
    paragraphs = text.split('\n\n')
    question_answer = {}
    question = None
    answer = None
    for paragraph in paragraphs:
        separate = paragraph.find('\n')
        new_paragraph = paragraph[separate+1:].replace('\n', ' ')
        if paragraph.startswith('Вопрос'):
            question = new_paragraph
        elif paragraph.startswith('Ответ'):
            answer = form_answer(new_paragraph)
            print(new_paragraph, answer, sep=' '*3)
        if question and answer:
            question_answer[question] = answer

    return question_answer


def get_random_question(dict_question_answer):
    return random.choice(list(dict_question_answer.keys()))


def get_dict_questions_answers():
    file = get_random_file()
    text = read_file(file)
    dict_question_answer = form_dict_questions_answers(text)
    return dict_question_answer


def main():
    get_dict_questions_answers()


if __name__ == '__main__':
    main()
