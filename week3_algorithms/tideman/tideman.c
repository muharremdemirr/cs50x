#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max number of candidates
#define MAX 9

// preferences[i][j] is number of voters who prefer i over j
int preferences[MAX][MAX];

// locked[i][j] means i is locked in over j
bool locked[MAX][MAX];

// Each pair has a winner, loser
typedef struct
{
    int winner;
    int loser;
} pair;

// Array of candidates
string candidates[MAX];
pair pairs[MAX * (MAX - 1) / 2];

int pair_count;
int candidate_count;

// Function prototypes
bool vote(int rank, string name, int ranks[]);
bool detect_cycle(int winner, int loser);
void record_preferences(int ranks[]);
void add_pairs(void);
void sort_pairs(void);
void lock_pairs(void);
void print_winner(void);

int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2)
    {
        printf("Usage: tideman [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1;
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i] = argv[i + 1];
    }

    // Clear graph of locked in pairs
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            locked[i][j] = false;
        }
    }

    pair_count = 0;
    int voter_count = get_int("Number of voters: ");

    // Query for votes
    for (int i = 0; i < voter_count; i++)
    {
        // ranks[i] is voter's ith preference
        int ranks[candidate_count];

        // Query for each rank
        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);

            if (!vote(j, name, ranks))
            {
                printf("Invalid vote.\n");
                return 3;
            }
        }

        record_preferences(ranks);

        printf("\n");
    }

    add_pairs();
    sort_pairs();
    lock_pairs();
    print_winner();
    return 0;
}

// Update ranks given a new vote
bool vote(int rank, string name, int ranks[])
{
    for (int i = 0; i < candidate_count; ++i)
    {
        if (strcmp(name, candidates[i]) == 0)
        {
            ranks[rank] = i;
            return true;
        }
    }

    return false;
}

// Update preferences given one voter's ranks
void record_preferences(int ranks[])
{
    for (int i = 0; i < candidate_count; ++i)
    {
        for (int j = i + 1; j < candidate_count; ++j)
        {
            ++preferences[ranks[i]][ranks[j]];
        }
    }
    return;
}

// Record pairs of candidates where one is preferred over the other
void add_pairs(void)
{
    for (int i = 0; i < candidate_count; ++i)
    {
        for (int j = i + 1; j < candidate_count; ++j)
        {
            if (preferences[i][j] > preferences[j][i])
            {
                pairs[pair_count].winner = i;
                pairs[pair_count].loser = j;
            }
            else if (preferences[i][j] < preferences[j][i])
            {
                pairs[pair_count].winner = j;
                pairs[pair_count].loser = i;
            }
            else
            {
                continue;
            }
            ++pair_count;
        }
    }
    return;
}

// Sort pairs in decreasing order by strength of victory
void sort_pairs(void)
{
    bool is_changed = false;
    int max;
    int max_loc = -1;
    pair temp;
    for (int i = 0; i < pair_count; ++i)
    {
        max = preferences[pairs[i].winner][pairs[i].loser] -
              preferences[pairs[i].loser][pairs[i].winner];
        for (int j = i + 1; j < pair_count; ++j)
        {
            int winner = pairs[j].winner;
            int loser = pairs[j].loser;
            int diff = preferences[winner][loser] - preferences[loser][winner];
            if (diff > max)
            {
                is_changed = true;
                max = diff;
                max_loc = j;
            }
        }
        if (is_changed)
        {
            // swap
            temp = pairs[i];
            pairs[i] = pairs[max_loc];
            pairs[max_loc] = temp;
            is_changed = false;
        }
    }

    return;
}

// Lock pairs into the candidate graph in order, without creating cycles
void lock_pairs(void)
{

    for (int i = 0; i < pair_count; ++i)
    {
        int winner = pairs[i].winner;
        int loser = pairs[i].loser;
        if (!detect_cycle(winner, loser))
        {
            locked[winner][loser] = true;
        }
    }

    return;
}

// Print the winner of the election
void print_winner(void)
{
    for (int i = 0; i < candidate_count - 1; ++i)
    {
        bool is_lost = false;
        for (int j = 0; j < candidate_count; ++j)
        {
            if (locked[j][i] && i != j) // if true lost at least once
            {
                is_lost = true; // has beaten
                break;
            }
        }
        if (!is_lost)
        {
            printf("%s\n", candidates[i]);
        }
    }
    return;
}
// Detects cycle
bool detect_cycle(int winner, int loser)
{
    if (winner == loser) // base, cycle
    {
        return true;
    }
    for (int i = 0; i < candidate_count; ++i)
    {
        if (locked[loser][i] && detect_cycle(winner, i))
        {
            return true;
        }
    }
    return false;
}
