'''
Script for tracking particle movement from a series of measurements.
Uses the trackpy library, which is specialized for tracking particles in
softmatter research. Exports partially processed data in an HDF5 file, and 
fully processed data in a CSV file.

USE:
- Call the turb.main(base_path) function from another script
- Simply run this script itself, editing the base_path argument below

base_path is the path to the folder containing multiple films using 
a specific file structure.
base_path
    |--Film1
    |   |--1
    |   |   |--images
    |   |--2
    |   |   |--images
    |   |--3
    |--Film2
    |   |--1
'''

import numpy as np
import pandas as pd
import pims
import trackpy as tp
tp.ignore_logging()
from skimage import data, color
from skimage.filters import threshold_local
import skimage
# warning.catch_warnings
import glob
import os
import sys
import cv2 as cv
from tkinter import filedialog, Tk
from joblib import Parallel, delayed


#User options#
THRESH = 134
crop = [0,00] #Distance from left and right to crop out


def main(base_path):
    # Identify all films recorded
    def warn(*args, **kwargs):
        pass
    import warnings
    warnings.warn = warn
    films = glob.glob(os.path.join(base_path , 'Film[1-9]'))
    if films != []:
        print('analyzing ', len(films), ' films')
        for film in films:
            dirnames = glob.glob(os.path.join(film, '[1-9]'))
            for number in dirnames:
                analyze_data(number, crop)        
    else:
        print("No films found. Check path to days' films")

# Takes in path to scene, saving results to .h5 file and .CSV file
def analyze_data(path, x_crop = [0,0]):
    print("Analyzing " + path)
    # Analyze scene images, filter out sparse data, and export data
    all_results = analyze_frames(path,x_crop)
    t1 = tp.filter_stubs(all_results,15)
    export_csv(t1, path)

def analyze_frames(number,x_crop):
    film = os.path.dirname(number)
    # Format image sequence for processing
    frames = pims.ImageSequence(number+'//*.bmp', as_grey = True)
    datastorename = os.path.join(film,'data-t'+number.strip()[-1]+'.h5')

    with tp.PandasHDFStoreBig(datastorename) as s:
        # Normalize the pictures to black and white, and identify islands
        normalize_pictures_parallel(frames,number,s,x_crop)
        print('\t Identifying tracks and linking...')

        # Connect and track particles. Saving tracks to 's'.
        pred = tp.predict.ChannelPredict(5,minsamples=3)
        for linked in pred.link_df_iter(s,6):
            s.put(linked)
        all_results=s.dump()
    return all_results


def normalize_pictures(frames, sequence, s, x_crop):
    num_frames = str(len(frames))
    for num, img in enumerate(frames):                                     
        print('\t Normalizing image ' + str(num + 1) + '/' + num_frames + '...\r', end='')
        features = normalize(num,img,sequence,x_crop)
        s.put(features)
    print('')   # Prevent progress message deletion


def normalize_pictures_parallel(frames, sequence, s, x_crop):
    features = Parallel(n_jobs=-2,verbose=1)(delayed(normalize)(num,img,sequence,x_crop) for num,img in enumerate(frames))
    for feature in features:
        s.put(feature)


def normalize(num,img,sequence,x_crop):
    # Identify islands in the image
    img = img[:,x_crop[0]:img.shape[1]-x_crop[1]]

    # block_size = 53
    # binary_adaptive = img > threshold_local(img, block_size, offset=12)
    # img = np.array(binary_adaptive,'uint8') * 255
    img = thresh(img)

    label_image,num_regions = skimage.measure.label(img, return_num=True)

    features = pd.DataFrame()
    # If only one artifact (the post), skip to next frame
    if num_regions <1:
        return features

    # Check quality of islands found, and save if good enough
    for region in skimage.measure.regionprops(label_image, intensity_image = img):
        if region.area <20 or region.area >10000:
            continue
        if region.mean_intensity ==0:
            continue
        if region.eccentricity > .78:
            continue
        features = features.append([{'y':region.centroid[0],
                            'x':region.centroid[1] + x_crop[0],
                            'area':region.area,
                            'frame':num,
                            'region': sequence,
                            'y_min': region.bbox[0],
                            'y_max': region.bbox[2],
                            'x_min': region.bbox[1] + x_crop[0],
                            'x_max': region.bbox[3] + x_crop[0],
                            #'eccentricity': region.eccentricity
                            }])
    return features


def thresh(img):
    # Set pixes to black or white according to the THRESH const
    """
    img[img<THRESH] = THRESH
    img[img>THRESH] = 255
    img[img==THRESH] = 0
    """
    img = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,11,2)
    return skimage.util.img_as_int(img)


def export_csv(t1, number):
    film = os.path.dirname(number)
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
        # TODO: see about not doing this step and appending directly. This is what's making the script so slow
        for x, y, dx, dy, dvr, area, frame, region, x_min, x_max, y_min, y_max in zip(sub.x[:-1], sub.y[:-1], dvx, dvy, dvr, sub.area[:-1], sub.frame[:-1],sub.region[:-1],sub.x_min[:-1],sub.x_max[:-1],sub.y_min[:-1],sub.y_max[:-1]):
            data = data.append([{'dx': dx,
                                'dy': dy,
                                'dr': dvr,
                                'x': x,
                                'y': y,
                                #'eccentricity': eccentricity,
                                'area':area,
                                'frame': frame,
                                'region': region,
                                'particle': item,
                                'x_min': x_min,
                                'x_max': x_max,
                                'y_min': y_min,
                                'y_max': y_max
                                }])
    # Export the DataFrame to the CSV file
    data.to_csv(os.path.join(film,'t'+number.strip()[-1]+'valuematrix.csv')) # Export saved data to CSV file
    print('')


if __name__ == '__main__':
    root = Tk()
    root.withdraw()
    directory = filedialog.askdirectory(initialdir=os.path.expanduser('~'))
    root.destroy()
    if directory != "":
        base_path = directory
    main(base_path)