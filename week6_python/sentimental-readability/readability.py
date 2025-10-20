from cs50 import get_string


def main():
    txt = get_string('Text: ')
    values = calc_values(txt)
    index = get_index(values)

    if index < 1:
        print("Before Grade 1")
    elif index >= 16:
        print("Grade 16+")
    else:
        print(f'Grade {index}')


def get_index(values):
    L = (values['letters'] / values['words']) * 100
    S = (values['sentences'] / values['words']) * 100
    index = 0.0588 * L - 0.296 * S - 15.8
    return round(index)


def calc_values(txt):
    values = {
        'words': 0,
        'letters': 0,
        'sentences': 0
    }
    count_words = 0
    count_sentences = 0
    count_letters = 0

    for digit in txt:
        if digit.isalpha():
            count_letters += 1
    values['letters'] = count_letters

    for i in txt:
        if i == ' ':
            count_words += 1
    values['words'] = count_words + 1

    for i in txt:
        if i in ['.', '!', '?']:
            count_sentences += 1
    values['sentences'] = count_sentences

    return values


main()
