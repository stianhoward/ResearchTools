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
from tkinter import filedialog
import glob

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.abspath('../tools'))
import file_interface as fi
sys.path.insert(0, os.path.abspath('../tracking'))
import tracker


def main(args):
    paths = fi.get_multi_paths()
    save_path = fi.get_directory("Select a save directory")
    if args.force == True:
        paths = recalculate(paths)
    bola_extraction(paths,save_path,args.border)


def recalculate(paths):
    for path in paths:
            temp = []
            try:
                tracker.main(path) 
                temp.append(path)
            except:
                print("Failed to process: ", path, sys.exc_info())
    return temp
    

def bola_extraction(paths, save_path, border):
    for path in paths:
        analyze_scene(path, save_path, border)
    return


# Input path to the folder containing Films
def analyze_scene(path, save_path, border):
    # Find the paths to CSV files in the films
    data_matrices = find_csv_paths(path)

    # Iterate through each CSV file
    for matrix in data_matrices:
        raw_data = fi.pd_import_csv(matrix)
        data = raw_data.loc[:,['particle', 'eccentricity', 'x_min', 'x_max', 'y_min', 'y_max', 'frame', 'region']]
        particles = np.unique(data.reset_index()['particle'].values)
        
        # Iterate through each particle
        for particle_id in particles:
            particle_data = data.loc[data['particle'] == particle_id]
            if check_bola(particle_data):
                slice_bolas(particle_data, border, os.path.dirname(matrix), save_path)
                save_bola_info(particle_id, particle_data, save_path, matrix)
 

def find_csv_paths(base_path):
    paths = []
    films = glob.glob(os.path.join(base_path, 'Film[1-9]'))
    for film in films:
        valuematrices = glob.glob(os.path.join(film, 't[1-9]valuematrix.csv'))
        for matrix in valuematrices:
            paths.append(matrix)
    return paths


# return True or False depending on whether or not bola conditions are met
def check_bola(particle_data):
    # Number of frames
    if len(np.unique(particle_data.reset_index()['frame'].values)) < 20:
        return False
    
    # Eccentricity decreasing
    ecc_min = particle_data['eccentricity'].min()
    min_frame = particle_data.loc[particle_data['eccentricity'] == ecc_min]['frame'].values[0]
    ecc_max = particle_data['eccentricity'].max()
    max_frame = particle_data.loc[particle_data['eccentricity'] == ecc_max]['frame'].values[0]
    if ecc_min > 0.1 or ecc_max < 0.7:
        return False
    if max_frame > min_frame:
        return False
    
    # Additional constraints
    return True


# Path is to the folder containing the Films
# save_path is to directory for bolas 
def slice_bolas(particle_data, border, path, save_path):
    frames = np.unique(particle_data.reset_index()['frame'].values)
    region = np.unique(particle_data.reset_index()['region'].values)[0]
    for frame in frames:
        # Determine paths for image and saving
        [save_path, image_path] = determin_directories(path, region, frame)
        image = fi.retrieve_image(image_path)

        #Crop and save the image to location
        frame_data = particle_data.loc[particle_data['frame'] == frame]
        image = image[frame_data['y_min']:frame_data['y_max'], frame_data['x_min']:frame_data['x_max']]
        fi.save_image(save_path, image)


def determin_directories(path, region, frame):
    # Path to save splices to
    tmp1 = os.path.split(region)
    tmp2 = os.path.split(tmp1[0])
    save_path = os.path.join(path, tmp2[1], tmp1[1], (str(frame+1) + '.bmp'))

    img_name = glob.glob(os.path.join(path, ("*" + ("00000" + str(frame+1))[-5:] + ".bmp")))
    image_path = os.path.join(path, tmp1[1], img_name[0])
    return (save_path, image_path)


def save_bola_info(particle_id, particle_data, save_path, matrix):
    with open(os.path.join(os.path.dirname(save_path), "info.txt"),'w') as file:
        file.wrine('Used CSV at: '+ matrix)
        file.write('CSV generated data at from: ' + np.unique(particle_data['region']))
        text = fi.load_txt(os.path.join(os.path.dirname(matrix), os.path.split(os.path.dirname(matrix))[1], 'position.txt'))
        if text == None:
            file.write('Position and flow info: Failed to locate position.txt file')
        else: 
            file.write('Position and flow info: '+ text)
        file.write('Frame range: '+ particle_data['frame'].min()+ ' - '+ particle_data['frame'].max())


def parse_arguments():
    parser = argparse.ArgumentParser(description='Identify and slice bolas.')
    parser.add_argument('--force', type=bool, help = "Force recalculation. WARNING: MAY TAKE A VERY LONG TIME!")
    parser.add_argument('--border', type=int, help = "Number of pixels to buffer image with.")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
