import random
import os
import os.path
from format_answer import form_answer


def get_random_file(directory='quiz-questions'):
    file = random.choice([file for file in os.listdir(directory) if file.endswith('.txt')])
    return os.path.join(directory, file)


def form_dict_questions_answers(file):
    with open(file, 'r', encoding='KOI8-R') as f:
        text = f.read()
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
        if question and answer:
            question_answer[question] = answer

    return question_answer


def get_dict_questions_answers():
    file = get_random_file()
    dict_question_answer = form_dict_questions_answers(file)
    return dict_question_answer


def main():
    get_dict_questions_answers()


if __name__ == '__main__':
    main()
