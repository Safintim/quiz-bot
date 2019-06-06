import re


def remove_text_with_brackets(text):
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\[.*?\]', '', text)

    return text


def remove_dots_one_after_another(text):
    return text.replace('...', '')


def remove_quotes(text):
    return text.replace('\'', '').replace('"', '')


def form_answer(answer):
    answer = remove_text_with_brackets(answer)
    answer = remove_quotes(answer)
    answer = remove_dots_one_after_another(answer)
    return answer.lower().strip('. ')
