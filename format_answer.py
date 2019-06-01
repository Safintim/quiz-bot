def remove_text_with_brackets(text):
    brackets = {
        '(': ')',
        '[': ']'
    }

    for br in brackets:
        open_bracket = text.find(br)
        while open_bracket >= 0:
            close_bracket = text.find(brackets[br])
            text = text[:open_bracket] + text[close_bracket+1:]
            open_bracket = text.find(br)

    return text


def remove_dots_one_after_another(text):
    pattern = '...'
    while pattern in text:
        text = text.replace(pattern, '')
    return text


def remove_dot_in_end_text(text):
    if text[len(text)-1] == '.':
        return text[:-1]
    return text


def remove_quotes(text):
    quotes = ['\'', '"']

    for symbol in text:
        if symbol in quotes:
            text = text.replace(symbol, '')
    return text


def form_answer(answer):
    answer = remove_text_with_brackets(answer)
    answer = remove_quotes(answer)
    answer = remove_dots_one_after_another(answer)
    answer = remove_dot_in_end_text(answer)
    return answer.lower().strip()
