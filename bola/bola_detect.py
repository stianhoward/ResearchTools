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
    if border == None:
        border = 10
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
        data = raw_data.loc[:,['particle', 'eccentricity', 'x_min', 'x_max', 'y_min', 'y_max', 'frame', 'region', 'area']]
        particles = np.unique(data.reset_index()['particle'].values)
        
        # Iterate through each particle
        for particle_id in particles:
            particle_data = data.loc[data['particle'] == particle_id]
            if check_bola(particle_data):
                slice_bolas(particle_data, border, save_path, os.path.dirname(matrix), particle_id)
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
    if ecc_min > 0.7 or ecc_max < 0.93:
        return False
    if max_frame > min_frame:
        return False
    
    if particle_data['area'].mean() < 100:
        return False
    
    # Additional constraints
    return True


# Path is to the folder containing the Films
# save_path is to directory for bolas 
def slice_bolas(particle_data, border, save_dir, path, particle_id):
    frames = np.unique(particle_data.reset_index()['frame'].values)
    region = np.unique(particle_data.reset_index()['region'].values)[0]
    for frame in frames:
        # Determine paths for image and saving
        [save_path, image_path] = determine_directories(path, save_dir, region, frame, particle_id)
        image = fi.retrieve_image(image_path)

        #Crop and save the image to location
        image = crop_image(image, particle_data, frame, border)
        fi.save_image(save_path, image)


def determine_directories(path, save_path, region, frame,particle_id):
    # Path to save splices to
    tmp1 = os.path.split(region)
    tmp2 = os.path.split(tmp1[0])
    tmp3 = os.path.split(tmp2[0])
    save_path = os.path.join(save_path, tmp3[1], tmp2[1], tmp1[1], str(particle_id), (str(frame+1) + '.jpg'))

    string = "??" + ("00000" + str(int(frame)+1))[-4:] + ".bmp"
    img_name = glob.glob(os.path.join(path, tmp1[1], string))
    image_path = os.path.join(path, tmp1[1], img_name[0])
    return (save_path, image_path)


def crop_image(image, particle_data, frame, border):
    frame_data = particle_data.loc[particle_data['frame'] == frame]
    size = image.shape
    y_min = frame_data['y_min'].values[0] - border
    if y_min < 0:
        y_min = 0
    y_max = frame_data['y_max'].values[0] + border
    if y_max > size[0]:
        y_max = size[0]
    x_min = frame_data['x_min'].values[0] - border
    if x_min < 0:
        x_min = 0
    x_max = frame_data['x_max'].values[0] + border
    if x_max > size[1]:
        x_max = size[1]
    image = image[y_min:y_max , x_min:x_max]
    return image
        


def save_bola_info(particle_id, particle_data, save_path, matrix):
    tmp1 = os.path.split(os.path.dirname(matrix))
    tmp2 = os.path.split(tmp1[0])
    save_path = os.path.join(save_path, tmp2[1], tmp1[1], matrix[-16], str(particle_id), "info.txt")
    with open(save_path,'w') as file:
        file.write(str('Used CSV at: '+ matrix + '\n'))
        file.write('CSV generated data at from: ' + str(np.unique(particle_data['region'])) + '\n')
        text = str(fi.load_txt(os.path.join(os.path.dirname(matrix), matrix[-16], 'position.txt')) + '\n')
        if text == None:
            file.write('Position and flow info: Failed to locate position.txt file' + '\n')
        else: 
            file.write('Position and flow info: '+ text + '\n')
        file.write(str('Frame range: '+ str(particle_data['frame'].min()) + ' - '+ str(particle_data['frame'].max())) + '\n')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Identify and slice bolas.')
    parser.add_argument('--force', type=bool, help = "Force recalculation. WARNING: MAY TAKE A VERY LONG TIME!")
    parser.add_argument('--border', type=int, help = "Number of pixels to buffer image with.")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments)
