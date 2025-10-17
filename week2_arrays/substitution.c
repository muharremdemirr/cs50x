#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>

bool isAlphabetic(string key);
bool anyDuplicate(string key);

int main(int argc, string argv[])
{
    string key = argv[1];
    if (argc == 2)
    {
        if (strlen(key) != 26)
        {
            printf("Key must contains 26 characters.");
            return 1;
        }
        else if (!isAlphabetic(key))
        {
            printf("Non-alphabetic\n");
            return 1;
        }
        else if (anyDuplicate(key))
        {
            printf("Duplicates\n");
            return 1;
        }
        else
        {
            string plainText = get_string("plaintext: ");
            int n = strlen(plainText);
            char cipherText[n + 1];
            for (int i = 0; i < n; ++i)
            {
                if (isalpha(plainText[i]))
                {
                    int index = toupper(plainText[i]) - 'A';
                    if (islower(plainText[i]))
                    {
                        cipherText[i] = tolower(key[index]);
                    }
                    else
                    {
                        cipherText[i] = toupper(key[index]);
                    }
                }
                else
                {
                    cipherText[i] = plainText[i];
                }
            }
            cipherText[n] = '\0';
            printf("ciphertext: %s\n", cipherText);
        }
    }
    else
    {
        printf("Usage: %s key\n", argv[0]);
        return 1;
    }
}

bool isAlphabetic(string key)
{
    for (int i = 0, n = strlen(key); i < n; ++i)
    {
        if (!isalpha(key[i]))
        {
            return false;
        }
    }
    return true;
}

bool anyDuplicate(string key)
{
    for (int i = 0, n = strlen(key); i < n - 1; ++i)
    {
        for (int j = i + 1; j < n; ++j)
        {
            if (toupper(key[i]) == toupper(key[j]))
            {
                return true;
            }
        }
    }
    return false;
}
