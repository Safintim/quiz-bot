import os
import os.path
from format_answer import form_answer


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
        if question and answer:
            question_answer[question] = answer

    return question_answer


def get_dicts_questions_answers(directory='quiz-questions'):
    for file in os.listdir(directory):
        with open(file, 'r', encoding='KOI8-R') as f:
            text = f.read()
        temp = form_dict_questions_answers(text)
        yield temp


def main():
    list(get_dicts_questions_answers())


if __name__ == '__main__':
    main()
