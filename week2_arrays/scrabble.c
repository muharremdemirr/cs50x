#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>

string toUpperCase(string word);
int getPoints(string word, char letters[], int points[], int length);

int main()
{
    int numOfLetters = 26;
    char letters[numOfLetters];
    letters[0] = 'A'; // first letter
    for (int i = 1; i < numOfLetters; ++i)
    {
        letters[i] = letters[0] + i;
        // here we add the turn of the letter at the alphabeth over the unicode 'A'
    }
    /*
    for(int i = 0; i < 26; ++i){
        printf("%c ", letters[i]);
    }
    */

    int points[] = {1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10};

    string player1 = get_string("Player 1: ");
    string player2 = get_string("Player 2: ");

    toUpperCase(player1);
    toUpperCase(player2); // since we used capital letters

    int firstPoints = getPoints(player1, letters, points, numOfLetters);
    int secondPoints = getPoints(player2, letters, points, numOfLetters);

    if (firstPoints > secondPoints)
    {
        printf("Player 1 wins!\n");
    }
    else if (firstPoints < secondPoints)
    {
        printf("Player 2 wins!\n");
    }
    else
    {
        printf("Tie!\n");
    }
}

string toUpperCase(string word)
{
    int i = 0;
    while (word[i] != '\0')
    {
        word[i] = toupper(word[i]);
        ++i;
    }
    return word;
}

int getPoints(string word, char letters[], int points[], int length)
{
    int result = 0;
    int i = 0;
    while (word[i] != '\0')
    {
        for (int j = 0; j < length; ++j)
        {
            if (word[i] == letters[j])
            {
                result += points[j]; // same index as letters
                break;               // don't need to look for it anymore
            }
        }
        ++i;
    }
    return result;
}
