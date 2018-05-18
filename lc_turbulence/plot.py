import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
mpl.rc('figure',  figsize=(10, 6))
mpl.rc('image', cmap='gray')
import numpy as np
import pandas as pd
from pandas import DataFrame, Series  #for convenience
from numpy.polynomial import polynomial as P
import glob
import argparse
import csv
import pylab as py
import scipy
import sys
FRAME_RATE= 8000        # FrameRate
PIXEL_SIZE=.0044     # mm per pixel

def main():
    base_path = '/media/stian/Evan Dutch/Turbulence/2018-05-17/'

    # Determine films in path
    films = glob.glob(base_path + 'Film[1-9]')
    for film in films:
        film = film + '/'
        valuematrices = glob.glob(film + 't[1-9]valuematrix.csv')
        for matrix in valuematrices:
            open_path = matrix
            save_path = film
            save_name = matrix.strip()[-16] + '.png'

            # save_path = film + '/racetest' + matrix.strip()[-16] + '.png'

            try:
                raw_data = pd.read_csv(open_path)        # Import a data set
                location = loadLocation(film + matrix.strip()[-16] + '/position.txt')
                scatter(raw_data, location, save_path, save_name)   # Create and save Scatter plot of data
                vector(raw_data, location, save_path, save_name)
            except:
                print("Unexpected error:", sys.exc_info())
                print("Failed to open and process data for: " + open_path)




def custom_round(x, base=20):
    return int(base * round(float(x)/base)) #this sets the width of the bins


def loadLocation(filePath):
    #Try to open info about file location in 'position.txt'
    try:
        file = open(filePath)
        location = file.read()
        location = location.strip()
        file.close()
    except:
        location = ''
        # Todo: Collect all of these to print at the end under one print.
        print("No 'position.txt' file found in: " + filePath)

    return location


def scatter(raw_data, location, save_path, save_name):
    yslice1 = raw_data.astype({'x':'int','y':'int'}) #set x and y values to integers

    yslice1['x']=yslice1['x'].apply(lambda x: custom_round(x, base=10))
    ygrouped1=yslice1.groupby(['x'],as_index=False).agg({'dr':['mean','std']})
    ygrouped1.columns=['x','dr','std']
    y1=ygrouped1.fillna(0) #replace NaNs with 0's

    x1=(-210+y1['x'])*PIXEL_SIZE    # Determin where the '210' value comes from. Potentially offset? half of width?
    dr1=y1['dr']*FRAME_RATE*PIXEL_SIZE      

    fig=plt.figure()
    ax=fig.add_subplot(111)

    ax.scatter(x1,dr1,color='r',label='0.31750 SLPM')

    plt.xlabel('Position',fontsize=20)
    plt.ylabel('Velocity (mm/s)',fontsize=20)
    plt.title(location + ': \nVelocity vs. Position',fontsize=20)
    ax.legend()
    fig.savefig(save_path + 'scatter' + save_name)
    plt.close()


def vector(raw_data, location, save_path, save_name):
    # Import desired elements
    raw_data = raw_data.astype({'x':'int','y':'int','dx':'float','dy':'float'})
    data = raw_data.loc[:,['x','y','dx','dy']]

    # Round values to bin sizes
    data['x'] = data['x'].apply(lambda x: custom_round(x, base = 50))
    data['y'] = data['y'].apply(lambda y: custom_round(y, base = 50))

    # Organize data for plot
    data = data.groupby(['x','y']).mean()
    data = data.reset_index()
    
    # Adjust for pixel size and framerate
    data.x = (data.x) * PIXEL_SIZE
    data.y = (data.y * -1 + data.y.values.max()) * PIXEL_SIZE
    data.dx = data.dx * FRAME_RATE * PIXEL_SIZE
    data.dy = data.dy * FRAME_RATE * PIXEL_SIZE * -1

    # Create and label plot
    plt.figure(figsize = (12,10))
    plt.title(location, fontsize = 45)
    plt.quiver(data['x'],data['y'],data['dx'],data['dy'])
    plt.xlabel('x-distance (mm)', fontsize = 30)
    plt.ylabel('y-distance (mm)', fontsize = 30)
    
    # Save Plot
    try:
        plt.savefig(save_path + 'vectorplot' + save_name)
    except:
        print("Unexpected error saving plot:", sys.exc_info())      



if __name__ == '__main__':
    main()