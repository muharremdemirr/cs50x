// check50 cs50/problems/2025/x/readability
#include <cs50.h>
#include <ctype.h>
#include <stdio.h>

float getWords(string text);
float getSentences(string text);
float getLetters(string text);

int main(void)
{
    string text = get_string("Text: ");
    float words = getWords(text);
    float letters = getLetters(text);
    float sentences = getSentences(text);

    float L = (letters / words) * 100.0;
    float S = (sentences / words) * 100.0;
    float index = (0.0588 * L) - (0.296 * S) - 15.8;

    if (index < 1)
    {
        printf("Before Grade 1\n");
    }
    else if (index >= 16)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %i\n", (int) (index + 0.5)); // rounded to the nearest integer.
    }
}

float getWords(string text)
{

    int words = 0;
    int index = 0;

    while (text[index] != '\0')
    {
        if (text[index] == ' ') // it's a word every word has ' ' after it except last one
        {
            ++words;
        }
        ++index;
    }
    return (float) (words + 1); // last word and make it float
}

float getLetters(string text)
{
    int letters = 0;
    int index = 0;

    while (text[index] != '\0')
    {
        if ((text[index] >= 'a' && text[index] <= 'z') || // if it's a lowercase letter or
            (text[index] >= 'A' && text[index] <= 'Z'))   // it's a capital letter
        {
            ++letters; // so it's a letter
        }
        ++index;
    }
    return (float) letters;
}

float getSentences(string text)
{

    int sentences = 0;
    int index = 0;

    while (text[index] != '\0')
    {
        if (text[index] == '.' || text[index] == '!' || text[index] == '?') // if it's senteneces
        {
            ++sentences;
        }
        ++index;
    }
    return (float) sentences;
}
