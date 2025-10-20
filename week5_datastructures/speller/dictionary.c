// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

// Choose number of buckets in hash table
const unsigned int N = 26;

// Hash table
node *table[N];

// Keep size of the table
unsigned int table_size = 0;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    int word_length = strlen(word);
    char lower[word_length + 1];

    for (int i = 0; i < word_length; ++i)
    {
        lower[i] = tolower(word[i]);
    }
    lower[word_length] = '\0';

    unsigned int word_hash = hash(lower);
    node *p = table[word_hash];

    while (p != NULL)
    {
        if (strcmp(p->word, lower) == 0)
        {
            return true;
        }
        p = p->next;
    }

    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    unsigned int word_hash = 0;
    for (int i = 0; word[i] != '\0'; i++)
    {
        word_hash = ((word_hash << 2) + word_hash) ^ word[i];
    }
    return word_hash % N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        return false;
    }

    char word[LENGTH + 1];

    while (fscanf(file, "%s", word) != EOF)
    {
        node *new_node = malloc(sizeof(node));
        if (new_node == NULL)
        {
            fclose(file);
            return false;
        }

        strcpy(new_node->word, word);
        new_node->next = NULL;

        unsigned int word_hash = hash(word);
        new_node->next = table[word_hash];
        table[word_hash] = new_node;

        ++table_size;
    }

    fclose(file);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    return table_size;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{

    for (int i = 0; i < N; ++i)
    {
        node *p = table[i];
        while (p != NULL)
        {
            node *tmp = p;
            p = p->next;
            free(tmp);
        }
    }
    return true;
}
