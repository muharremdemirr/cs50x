
def is_valid(card_number):
    card_number = int(card_number)
    is_not = True
    res = 0

    while card_number > 0:
        if is_not:
            is_not = False
            res += card_number % 10
        else:
            is_not = True
            digit = 2 * (card_number % 10)
            while digit > 0:
                res += digit % 10
                digit //= 10

        card_number //= 10
    if res % 10 == 0:
        return True
    return False


def decide_card(card_number):
    length = len(card_number)
    start = card_number[0:2]
    start_int = int(start)

    if length == 15 and (start == '34' or start == '37'):
        return 'AMEX'
    elif (length == 13 or length == 16) and start[0] == '4':
        return 'VISA'
    elif length == 16 and (start_int >= 51 and start_int <= 55):
        return 'MASTERCARD'
    return none

