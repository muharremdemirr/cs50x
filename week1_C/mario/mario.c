#include <cs50.h>
#include <stdio.h>

void printMario(int height);

int main(void)
{
    int height;
    do
    {
        height = get_int("Height: ");
    }
    while(height < 1);
    printMario(height);
}

void printMario(int height)
{

    for (int i = 0; i < height; ++i)
    {
        for (int j = 0; j < height; ++j)
        {
            if (j < height - i - 1)
            {
                printf(" ");
            }
            else
            {
                printf("#");
            }
        }
        printf("  ");

        for (int j = height; j > 0; --j)
        {
            if (j > height - i - 1)
            {
                printf("#");
            }
            else
            {
                break;
            }
        }

        printf("\n");
    }
}
