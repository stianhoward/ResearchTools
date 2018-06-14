'''
Script for tracking particle movement from a series of measurements.
Uses the trackpy library, which is specialized for tracking particles in
softmatter research. Exports partially processed data in an HDF5 file, and 
fully processed data in a CSV file.

USE:
- Call the turb.main(base_path) function from another script
- Simply run this script itself, editing the base_path argument below

base_path is the path to the folder containing multiple films using 
the labs normal file structure.
'''

import numpy as np
import pandas as pd
import pims
import trackpy as tp
tp.ignore_logging()
from skimage import data, color
import skimage
import glob
import os
import sys
from tkinter import filedialog, Tk
from joblib import Parallel, delayed
from timeit import default_timer as timer


#User options#
THRESH = 60
#Folder to analyze
# base_path = '/media/stian/Evan Dutch/Turbulence/2018-05-21/'
base_path = '/home/stian/Desktop/2018-05-23/'


def main(base_path):
    # Identify all films recorded
    films = glob.glob(os.path.join(base_path , 'Film[1-9]'))
    if films != []:
        print(films)
        for film in films:
            film = film + '/'
            # Identify, and iterate through, scenes for each film
            dirnames = glob.glob(os.path.join(film + '[1-9]'))
            for number in dirnames:
                print("Analyzing " + number)
                # Analyze scene images, filter out sparse data, and export data
                all_results = analyze_frames(film, number)
                t1 = tp.filter_stubs(all_results,10)
                export_csv(t1, film, number)                
    else:
        print("No films found. Check path to days' films")


def analyze_frames(film, number):
    # Format image sequence for processing
    frames = pims.ImageSequence(number+'//*.bmp', process_func=thresh)
    datastorename = film+'data-t'+number.strip()[-1]+'.h5'

    with tp.PandasHDFStoreBig(datastorename) as s:
        # Normalize the pictures to black and white, and identify islands
        start = timer()
        normalize_pictures_parallel(frames,number,s)
        end = timer()
        print(end-start)
        print('\t Identifying tracks and linking...')

        # Connect and track particles. Saving tracks to 's'.
        pred = tp.predict.ChannelPredict(10,minsamples=3)
        for linked in pred.link_df_iter(s,15):
            s.put(linked)
        all_results=s.dump()
    return all_results


def thresh(img):
    # Set pixes to black or white according to the THRESH const
    img[img<THRESH] = 0
    img[img>THRESH] = 255
    return skimage.util.img_as_int(img)


def normalize_pictures_parallel(frames, sequence, s):
    features = Parallel(n_jobs=-2,verbose=1)(delayed(normalize)(num,img,sequence) for num,img in enumerate(frames))
    for feature in features:
        s.put(feature)


def normalize(num,img,sequence):
    # Identify islands in the image
    label_image,num_regions = skimage.measure.label(img, return_num=True)

    features = pd.DataFrame()
    # If only one artifact (the post), skip to next frame
    if num_regions <1:
        return features

    # Check quality of islands found, and save if good enough
    for region in skimage.measure.regionprops(label_image, intensity_image = img):
        if region.area <20 or region.area >900000:
            continue
        if region.mean_intensity ==255:
            continue
        if region.eccentricity > .78:
            continue
        features = features.append([{'y':region.centroid[0],
                            'x':region.centroid[1],
                            'area':region.area,
                            'frame':num,
                            'region': sequence }])
    return features


def normalize_pictures(frames, sequence, s):
    num_frames = str(len(frames))
    for num, img in enumerate(frames):                                     
        print('\t Normalizing image ' + str(num + 1) + '/' + num_frames + '...\r', end='')
        features = normalize(num,img,sequence)
        '''
        # Identify islands in the image
        label_image,num_regions = skimage.measure.label(img, return_num=True)

        # If only one artifact (the post), skip to next frame
        if num_regions <1:
            break
        features = pd.DataFrame()

        # Check quality of islands found, and save if good enough
        for region in skimage.measure.regionprops(label_image, intensity_image = img):
            if region.area <20 or region.area >900000:
                continue
            if region.mean_intensity ==255:
                continue
            if region.eccentricity > .78:
                continue
            features = features.append([{'y':region.centroid[0],
                                'x':region.centroid[1],
                                'frame':num,
                                'region': number }])
        '''
        s.put(features)
    print('')   # Prevent progress message deletion


def export_csv(t1, film, number):
    data = pd.DataFrame()
    num_particles = str(len(set(t1.particle)))
    i = 0

    # Format data so other scripts can read the CSV
    for item in set(t1.particle):
        i = i + 1
        print('\t exporting particle ' + str(i) + '/' + num_particles + '...\r', end='')
        # Ensure image order for particle, and calcualte some values of interest
        sub = t1[t1.particle==item].sort_values('frame')
        dvx = np.diff(sub.x)
        dvy = np.diff(sub.y)
        dvr = np.sqrt(dvx**2+dvy**2)
        # Insert the data into the DataFrame
        for x, y, dx, dy, dvr, area, frame, region in zip(sub.x[:-1], sub.y[:-1], dvx, dvy, dvr, sub.area[:-1], sub.frame[:-1],sub.region[:-1]):
            data = data.append([{'dx': dx,
                                'dy': dy,
                                'dr': dvr,
                                'x': x,
                                'y': y,
                                'area':area,
                                'frame': frame,
                                'region': region,
                                'particle': item,
                                }])
    # Export the DataFrame to the CSV file
    data.to_csv(film+'t'+number.strip()[-1]+'valuematrix.csv') # Export saved data to CSV file
    print('')


if __name__ == '__main__':
    root = Tk()
    root.withdraw()
    directory = filedialog.askdirectory()
    root.destroy()
    if directory != "":
        base_path = directory
    main(base_path)