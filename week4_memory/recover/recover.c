#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>


int main(int argc, char *argv[])
{
    // Accept a single command-line argument
    if (argc != 2)
    {
        printf("Usage: ./recover FILE\n");
        return 1;
    }
    int block_size = 512;
    // Open the memory card
    char *memorycard_file = argv[1]; // created file_name to make it more readable
    FILE *file = fopen(memorycard_file, "r");

    if (file == NULL)
    {
        printf("Could not open file.\n");
        return 1;
    }

    mkdir("recovered", 0777);
    bool is_found = false;
    FILE *img = NULL;
    // While there's still data left to read from the memory card
    int file_number = 0;
    unsigned char buffer[block_size];
    while (fread(buffer, sizeof(buffer[0]), block_size, file) == block_size)
    {
        // new JPG
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff &&
            (buffer[3] & 0xf0) == 0xe0)
        {
            if (img != NULL) // if created a file
            {
                fclose(img);
            }

            is_found = true; // first file found

            // Create JPEGs from the data
            char jpg_file[18]; // 000.jpg\0
            sprintf(jpg_file, "recovered/%03i.jpg", file_number);
            img = fopen(jpg_file, "w");

            ++file_number;
        }
        if (is_found)
        {
            fwrite(buffer, sizeof(buffer[0]), block_size, img);
        }
    }
    if (img != NULL)
    {
        fclose(img);
    }
    fclose(file);
}
