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
f1=1000     # Not sure what this is. Needs investigation
mp=.0041033 # mm per pixel

def main():
    base_path = '/media/stian/Evan Dutch/Turbulence/2018-05-17/'
    # Determine films in path
    films = glob.glob(base_path + 'Film[1-9]')
    for film in films:
        film = film + '/'
        valuematrices = glob.glob(film + 't[1-9]valuematrix.csv')
        for matrix in valuematrices:
            open_path = matrix
            save_path = film + '/racetest' + matrix.strip()[-16] + '.png'

            try:
                rawData = pd.read_csv(open_path) # Import a data set
                location = loadLocation(film + matrix.strip()[-16] + '/position.txt')
                scatter(rawData, location, save_path) # Create and save Scatter plot of data
            except:
                print("Failed to open data for: " + open_path)




def custom_round(x, base=20):
    return int(base * round(float(x)/base)) #this sets the width of the bins


def loadLocation(filePath):
    #Try to open info about file location in 'position.txt'
    try:
        file = open(filePath)
        location = file.read()
        location = location.strip() + ': '
        file.close()
    except:
        location = ''
        # Todo: Collect all of these to print at the end under one print.
        print("No 'position.txt' file found in: " + filePath)

    return location


def scatter(rawData, location, save_path):
        yslice1 = rawData.astype({'x':'int','y':'int'}) #set x and y values to integers

        yslice1['x']=yslice1['x'].apply(lambda x: custom_round(x, base=10))
        ygrouped1=yslice1.groupby(['x'],as_index=False).agg({'dr':['mean','std']})
        ygrouped1.columns=['x','dr','std']
        y1=ygrouped1.fillna(0) #replace NaNs with 0's

        x1=(-210+y1['x'])*mp
        dr1=y1['dr']*f1*mp

        fig=plt.figure()
        ax=fig.add_subplot(111)

        ax.scatter(x1,dr1,color='r',label='0.31750 SLPM')

        plt.xlabel('Position',fontsize=20)
        plt.ylabel('Velocity (mm/s)',fontsize=20)
        plt.title(location + '\nVelocity vs. Position',fontsize=20)
        ax.legend()
        fig.savefig(save_path)


if __name__ == '__main__':
    main()