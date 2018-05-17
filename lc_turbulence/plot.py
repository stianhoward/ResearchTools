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
f1=1000
mp=.0041033 #mm per pixel

base_path = '/media/stian/Evan Dutch/Turbulence/2018-05-15/'
#Determine films in path
films = glob.glob(base_path + 'Film[1-9]')
for film in films:
    film = film + '/'
    valuematrices = glob.glob(film + 't[1-9]valuematrix.csv')
    for matrix in valuematrices:
        open_path = matrix
        save_path = film + '/racetest' + matrix.strip()[-16] + '.png'

        #Try to open info about file location in 'position.txt'
        try:
            file = open(film + matrix.strip()[-16] + '/position.txt')
            area = file.read()
            area = area.strip() + ': '
            file.close()
        except:
            area = ''


        oldstuff = pd.read_csv(open_path) #import a data set
        yslice1 = oldstuff.astype({'x':'int','y':'int'}) #set x and y values to integers

        def custom_round(x, base=20):
            return int(base * round(float(x)/base)) #this sets the width of the bins

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
        plt.title(area + '\nVelocity vs. Position',fontsize=20)
        ax.legend()
        fig.savefig(save_path)