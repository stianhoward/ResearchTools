
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


# Optionally, tweak styles.
mpl.rc('figure',  figsize=(10, 6))
mpl.rc('image', cmap='gray')

import numpy as np
import pandas as pd
from pandas import DataFrame, Series  # for convenience

import pims
import trackpy as tp
# from IPython.html.widgets import interact, interactive, fixed
from ipywidgets import interact, interactive, fixed
from skimage import data, color
import skimage
from skimage.transform import hough_circle
from skimage.feature import peak_local_max
from skimage.draw import circle_perimeter
from skimage.util import img_as_ubyte
from skimage.filters import threshold_otsu, threshold_adaptive
#import av
from skimage import morphology, util
from scipy.ndimage.interpolation import rotate
import trackpy.predict
from scipy.optimize import fmin
import glob
import argparse
import os
import sys


#User options#
#Folder to analyze
path = '/media/stian/Evan Dutch/Turbulence/2018-05-17/'

#add in command line arguments for debugging
parser = argparse.ArgumentParser(description='Fragile program for analyzing and stiching together data for the nozzle experiment')

parser.add_argument('analyze', help = 'do you want to analyze the raw data? true/false', type =int)


args = parser.parse_args()

if args.analyze==1:
    films = glob.glob(path + 'Film[1-9]')
    print(films)
    for film in films:
        film = film + '/'

        print('analyzing ' + film)
        dirnames = glob.glob(film + '[1-9]')
        #should be numbers 1 through 9, one for each region

        def thresh(img):
            #determine threshold values from imagej
            img[img<45] = 0
            img[img>45] = 255
            return util.img_as_int(img)
        '''
        def detect(num, img):
            label_image,num_regions = skimage.measure.label(img, return_num=True)
            if num_regions <1:
                raise ValueError('No Regions')
                #print num_regions
            features = pd.DataFrame()

            for region in skimage.measure.regionprops(label_image, intensity_image = img):
                if region.area <10 or region.area >900000:
                    continue
                if region.mean_intensity ==255:
                    continue
                if region.eccentricity > .78:
                    continue
                features = features.append([{'y':region.centroid[0],
                                            'x':region.centroid[1],
                                            'frame':num}])
            return features
            '''

        BigData = [] #list to hold data from all the regions
        for number in dirnames:
            frames = pims.ImageSequence(number+'//*.bmp', process_func=thresh)
            
            datastorename = film+'data-t'+number.strip()[-1]+'.h5'
            with tp.PandasHDFStoreBig(datastorename) as s:
                for num, img in enumerate(frames):
                    print(num)
                    label_image,num_regions = skimage.measure.label(img, return_num=True)
                    if num_regions <1:
                        break
                    #print num_regions
                    features = pd.DataFrame()

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
            
                    s.put(features)
                pred = trackpy.predict.ChannelPredict(10,minsamples=3)
                for linked in pred.link_df_iter(s,15):
                    s.put(linked)

                all_results=s.dump()

            t1 = tp.filter_stubs(all_results,10)

            data = pd.DataFrame()
            for item in set(t1.particle):
                sub = t1[t1.particle==item].sort_values('frame') #just to make sure that subsequent frames are still next to each other after copy
                dvx = np.diff(sub.x)
                dvy = np.diff(sub.y)
                dvr = np.sqrt(dvx**2+dvy**2)

                for x, y, dx, dy, dvr, frame, region in zip(sub.x[:-1], sub.y[:-1], dvx, dvy, dvr, sub.frame[:-1],sub.region[:-1]):
                    data = data.append([{'dx': dx,
                                        'dy': dy,
                                        'dr': dvr,
                                        'x': x,
                                        'y': y,
                                    
                                        'frame': frame,
                                        'region': region,
                                        'particle': item,
                                        }])

            data.to_csv(film+'t'+number.strip()[-1]+'valuematrix.csv')
            BigData.append(data)
        
#Now, stich everything together.

#First split everything apart by region (the reason I don't do this before is to maintain a clear distinction between the 'raw' data and the processed data. So if something goes wrong, you can at least look at the raw .csv files.
if args.analyze == False:
    #read in csv file names
    BigData = []
    filenames = glob.glob('t*[0-9]*.csv')
    for name in filenames:
        temp = pd.read_csv(name, sep=',')
        BigData.append(temp)
