'''
Script for identifying bolas in the output files from tracker.py

Bolas are only identified if they start with a high eccentricity, which
then decreased towards thei end of life in the dataset. 

Input:
- CSV file containing particle information from tracker.py
 Output:
 - Directory containing structured images of only the particles in question
    - Images to be sorted by Data_Date -> Film -> Scene -> Particle ->
- .TXT file containing relevant information about the original dataset
    - Source directory (contains Date, film, scene etc)
    - Flow Rate / Position according to post
    - Frame range of the images
'''


def main():
    return


if __name__ == '__main__':
    main()