#include "helpers.h"
#include <math.h>
#include <string.h>

int limit(int value); // limitin max rgb

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{

    for (int i = 0; i < height; ++i)
    {
        for (int j = 0; j < width; ++j)
        {
            int avg = round(
                (float) ((image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) /
                         3.0));
            // rounded to the nearest also we can technique to add 0.5 and cast into int
            image[i][j].rgbtBlue = avg;
            image[i][j].rgbtGreen = avg;
            image[i][j].rgbtRed = avg;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE tmp;
    for (int i = 0; i < height; ++i)
    {
        for (int j = 0, k = width - 1; j < width / 2; ++j, --k)
        {
            tmp = image[i][j];
            image[i][j] = image[i][k];
            image[i][k] = tmp;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE tmp[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int total_red = 0;
            int total_green = 0;
            int total_blue = 0;
            int counter = 0; // neighbours

            for (int k = -1; k < 2; k++)
            {
                int row = i + k;
                if (row < 0 || row >= height) // if out of rows bounds
                {
                    continue;
                }

                for (int l = -1; l < 2; l++)
                {
                    int col = j + l;
                    if (col < 0 || col >= width) // if out of columns bounds
                    {
                        continue;
                    }

                    total_red += image[row][col].rgbtRed;
                    total_green += image[row][col].rgbtGreen;
                    total_blue += image[row][col].rgbtBlue;
                    counter++;
                }
            }

            tmp[i][j].rgbtRed = round((float) total_red / counter);
            tmp[i][j].rgbtGreen = round((float) total_green / counter);
            tmp[i][j].rgbtBlue = round((float) total_blue / counter);
        }
    }
    // write tmp on the image or cpy onto
    memcpy(image, tmp, sizeof(RGBTRIPLE) * height * width);
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE tmp[height][width];

    int Gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++) // image
        {
            int red_x = 0;
            int green_x = 0;
            int blue_x = 0;
            int red_y = 0;
            int green_y = 0;
            int blue_y = 0;

            for (int k = -1; k < 2; k++) // pixel
            {
                int row = i + k;
                if (row < 0 || row >= height) // if out of rows bounds
                {
                    continue;
                }

                for (int l = -1; l < 2; l++) // pixel
                {
                    int col = j + l;
                    if (col < 0 || col >= width) // if out of columns bounds
                    {
                        continue;
                    }

                    red_x += image[row][col].rgbtRed * Gx[k + 1][l + 1];
                    red_y += image[row][col].rgbtRed * Gy[k + 1][l + 1];

                    green_x += image[row][col].rgbtGreen * Gx[k + 1][l + 1];
                    green_y += image[row][col].rgbtGreen * Gy[k + 1][l + 1];

                    blue_x += image[row][col].rgbtBlue * Gx[k + 1][l + 1];
                    blue_y += image[row][col].rgbtBlue * Gy[k + 1][l + 1];
                }
            }
            tmp[i][j].rgbtRed = limit(round(sqrt((red_x * red_x) + (red_y * red_y))));
            tmp[i][j].rgbtGreen = limit(round(sqrt((green_x * green_x) + (green_y * green_y))));
            tmp[i][j].rgbtBlue = limit(round(sqrt((blue_x * blue_x) + (blue_y * blue_y))));
        }
    }
    // write tmp on the image or cpy onto
    memcpy(image, tmp, sizeof(RGBTRIPLE) * height * width);
    return;
}

int limit(int value)
{
    return value > 255 ? 255 : value;
}
