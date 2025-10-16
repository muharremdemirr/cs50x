#include <cs50.h>
#include <stdbool.h>
#include <stdio.h>

bool checkCard(long cardNumber);
string decideWhichCard(long cardNumber);
int checkFirstDigits(long cardNumber);
int countDigit(long cardNumber);

int main(void)
{

    long cardNumber;

    cardNumber = get_long("Number: ");
    if (checkCard(cardNumber))
    {
        string card = decideWhichCard(cardNumber);
        printf("%s\n", card);
        return 0;
    }
    printf("INVALID\n");
}
// American Express uses 15-digit numbers, start with 34 or 37
// MasterCard uses 16-digit numbers, and start with 51, 52, 53, 54, or 55
// Visa uses 13- and 16-digit numbers, starts with 4

string decideWhichCard(long cardNumber)
{
    int lenOf = countDigit(cardNumber);
    int md = checkFirstDigits(cardNumber);
    // printf("len of %i ", lenOf);
    // printf("md %i ", md);
    if (lenOf == 15 && (md == 34 || md == 37))
    {
        return "AMEX";
    }
    else if (lenOf == 16 && (md >= 51 && md <= 55)) // betwwen 51 and 55
    {
        return "MASTERCARD";
    }
    else if (((lenOf == 13 || lenOf == 16) && md / 10 == 4))
    {
        return "VISA";
    }
    return "INVALID";
}

int checkFirstDigits(long cardNumber)
{
    while (cardNumber >= 100)
    {
        cardNumber /= 10;
    }
    return cardNumber;
}
int countDigit(long cardNumber)
{
    int counter = 0;
    while (cardNumber > 0)
    {
        counter++;
        cardNumber /= 10;
    }
    return counter;
}

bool checkCard(long cardNumber)
{

    bool multiply = false;
    int total = 0;
    while (cardNumber >= 1)
    {

        if (multiply)
        {
            int mulByTwo = (cardNumber % 10) * 2;
            while (mulByTwo >= 1)
            {
                total += mulByTwo % 10;
                mulByTwo /= 10;
            }
        }
        else
        {
            int notMulByTwo = (cardNumber % 10);
            while (notMulByTwo >= 1)
            {
                total += notMulByTwo % 10;
                notMulByTwo /= 10;
            }
        }
        cardNumber /= 10;
        multiply = !multiply;
    }

    return (total % 10 == 0);
}
