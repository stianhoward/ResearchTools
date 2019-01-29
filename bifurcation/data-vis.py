#Program to display a 3D plot of the energy landscape from the PIV results

import numpy as np
import pandas as pd
import glob as glob
import matplotlib as mpl
import matplotlib.pyplot as plt
import re as re
import os
from scipy.interpolate import griddata


def analyze(baseroute, location, folder):
    os.chdir(baseroute + location + folder + '/')
    fileNames = glob.glob("*.txt")
    frameSearch = re.compile(folder + '_(\d{4}).txt')
    data = []
    #the first four columns are the most important
    cols =['x', 'y', 'u', 'v','SNR','valid','filtered','avg. intensity'] 
    nanTest = '       nan'
    for name in fileNames:
        temp = pd.read_csv(name,sep='\t',header=0,names = cols,na_values =nanTest)
        temp['filename'] = name
        temp['frame'] = int(frameSearch.match(name)[1])
        data.append(temp)

    data = pd.concat(data)
    data = data[data['filtered']==0]
    data['y'] = data['y'].max() - data['y'] + 15
    data['v'] = data['v']
    groups = data.groupby(['x','y'])
    aveData = groups.agg('mean')
    vel = aveData['u']**2+aveData['v']**2
    valueVel = vel[~vel.isnull()]
    #valueVel=valueVel[np.abs(valueVel)<4]
    keys = valueVel.keys()
    pts = np.array([(k[0],k[1]) for k in keys])
    xSpace = np.linspace(0,data['x'].max(),200)
    ySpace = np.linspace(0,data['y'].max(),200)
    velGrid = griddata( (pts[:,0],pts[:,1]), valueVel, (xSpace[None,:],ySpace[:,None]),method='cubic')
    levels = np.linspace(0,4,30)
    plt.contourf(xSpace[::1], ySpace[::-1],velGrid,levels=levels)
    plt.colorbar()

    #now, plot this over the frame image
    plt.subplots()
    im = mpl.image.imread(glob.glob('*.bmp')[0])
    aveDataFiltered=aveData.loc[keys]
    plt.quiver(aveDataFiltered.index.get_level_values(0),aveDataFiltered.index.get_level_values(1),aveDataFiltered['u'],aveDataFiltered['v'])
    plt.imshow(im,alpha=.5)
    plt.show()
    #now, try to grid this and make a contour plot
    '''
    def velGrid(x,y):
        try:
            return valueVel[x,y]
        except KeyError:
            return 0.
    '''


#First, read in the data

baseroute = '/home/stian/Desktop/Bifurcation/output/'
location = 'back/'
folder = '2851'
analyze(baseroute, location, folder)

