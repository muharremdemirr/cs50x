from cs50 import get_int
while True:
    h = get_int("Height: ")
    if h > 0 and h < 9:
        break


for i in range(h):
    for j in range(h):
        if j < h - i - 1:
            print(' ', end='')
        else:
            print('#', end='')

    print('  ', end='')

    for k in range(i + 1):
        print('#', end='')

    print()
