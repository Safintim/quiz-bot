def remove_text_with_brackets(text):
    brackets = {
        '(': ')',
        '[': ']'
    }

    for br in brackets:
        open_bracket = text.find(br)
        while open_bracket >= 0:
            close_bracket = text.find(brackets[br])
            if close_bracket >= 0:
                text = text[:open_bracket] + text[close_bracket+1:]
            else:
                text = text[:open_bracket]
            open_bracket = text.find(br)

    return text


def remove_dots_one_after_another(text):
    pattern = '...'
    while pattern in text:
        text = text.replace(pattern, '')
    return text


def remove_quotes(text):
    return text.replace('\'', '').replace('"', '')


def form_answer(answer):
    answer = remove_text_with_brackets(answer)
    answer = remove_quotes(answer)
    answer = remove_dots_one_after_another(answer)
    return answer.lower().strip('. ')
