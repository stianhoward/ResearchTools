
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


#User options#
THRESH = 40
#Folder to analyze
path = '/media/stian/Evan Dutch/Turbulence/2018-05-21/'
# path = '/home/stian/Desktop/test/'


def main():
    films = glob.glob(path + 'Film[1-9]')               # Find all films recorded
    if films != []:     # Ensure folders are actually found
        print(films)
        for film in films:                              # Iterate through found films
            film = film + '/'
            dirnames = glob.glob(film + '[1-9]')    
            for number in dirnames:                     # Iterate through scenes of films
                print("Analyzing " + number)
                all_results = analyze_frames(film, number)
                t1 = tp.filter_stubs(all_results,10)    # Particle information
                export_csv(t1, film, number)
    else:
        print("No films found. Check path to days' films")


def analyze_frames(film, number):
    frames = pims.ImageSequence(number+'//*.bmp', process_func=thresh)
    datastorename = film+'data-t'+number.strip()[-1]+'.h5'
    with tp.PandasHDFStoreBig(datastorename) as s:
        normalize_picture(frames, number, s)              # Normalize the pictures to black and white
        print('\t Identifying tracks and linking...')
        pred = tp.predict.ChannelPredict(10,minsamples=3)

        # Save data into HDFS5 file
        for linked in pred.link_df_iter(s,15):
            s.put(linked)
        all_results=s.dump()
    return all_results


def thresh(img):
    #determine threshold values from imagej
    img[img<THRESH] = 0
    img[img>THRESH] = 255
    return skimage.util.img_as_int(img)


def normalize_picture(frames, number, s):
    num_frames = str(len(frames))
    for num, img in enumerate(frames):
        print('\t Normalizing image ' + str(num + 1) + '/' + num_frames + '...\r', end='')
        
        label_image,num_regions = skimage.measure.label(img, return_num=True)

        if num_regions <1:
            break
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
    print('')   # Insert a New Line so not delete previous stuff


def export_csv(t1, film, number):
    # print('\t exporting to CSV file...')
    data = pd.DataFrame()
    num_particles = str(len(set(t1.particle)))
    i = 0
    for item in set(t1.particle):
        i = i + 1
        print('\t exporting particle ' + str(i) + '/' + num_particles + '...\r', end='')
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
    print('')


if __name__ == '__main__':
    main()