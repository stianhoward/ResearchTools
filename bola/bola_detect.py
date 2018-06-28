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

import argparse
import os
import sys

'''
sys.path.insert(0, os.path.abspath('../tracking'))

import tracker
'''

def main(args):
    if args.force is None:
        print('here')
    elif args.force == True:
        print('2') 
    print(arguments)
    return


def parse_arguments():
    parser = argparse.ArgumentParser(description='Identify and slice bolas.')
    parser.add_argument('--force', type=bool, help = "Force recalculation. Default = False")
    parser.add_argument('--border', type=int, help = "Number of pixels to buffer image with.")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
