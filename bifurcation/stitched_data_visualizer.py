import numpy as np
import pandas as pd
import glob as glob
import matplotlib as mpl
import matplotlib.pyplot as plt
import re as re
import os
from scipy.interpolate import griddata


def readFiles (path, files):
    os.chdir(path)
    fileNames = glob.glob("*.txt")
    frameSearch = re.compile(files)
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
    return data

def centerSpeeds(data, title = 'VectorPlot'):
    data = data.copy()
    # Function used in setting bin widths
    def custom_round(x, base=20):
        return int(base * round(x/base)) 
    
    # Sort the data
    data = data[data['filtered']==0]

    # Set data to 35 pixel chunks
    base = 20

    #data['x'] = data['x'].apply(lambda x: custom_round(x, base = 35))
    #data['x'].apply(lambda x: custom_round(x, base = 40))
    #data.x = base * round(data.x/base)
    #data.loc[:,'x'] = base * round(data.x/base)
    data.loc[:,'x'] = data['x'].map(lambda x: custom_round(x, base))
    #data['y'] = data['y'].apply(lambda y: custom_round(y, base = 35))
    #data.loc[:,'y'].apply(lambda y: custom_round(y, base = 35))
    #data.y = base * round(data.y/base)
    #data.loc[:,'y'] = base * round(data.y/base)
    data.loc[:,'y'] = data['y'].map(lambda y: custom_round(y,base))

    # Organize the data by x and y, averaging velocities
    data = data.groupby(['y','x']).mean()
    data = data.reset_index()
    data = data.fillna(0)

    # Create the x and velocity arrays
    y_selected = data[data['y'] == 400]
    x = y_selected['x']
    velocities = np.sqrt(np.square(y_selected['u'])  + np.square(y_selected['v']))

    # Plot the data
    plt.figure(2)
    plt.plot(x,velocities)
    plt.title(title)
    plt.show()
    

def vectorPlot(data, imagePath, title = 'VectorPlot'):
    # Import background image
    os.chdir(imagePath)
    im = mpl.image.imread(glob.glob('*.bmp')[0])

    # Sort the data
    data = data[data['filtered']==0]

    groups = data.groupby(['x','y'])
    aveData = groups.agg('mean')
    vel = aveData['u']**2+aveData['v']**2
    valueVel = vel[~vel.isnull()]
    valueVel=valueVel[np.abs(valueVel)<3]
    keys = valueVel.keys()

    # Plot the data
    plt.figure(1)
    aveDataFiltered=aveData.loc[keys]
    plt.quiver(aveDataFiltered.index.get_level_values(0),aveDataFiltered.index.get_level_values(1),aveDataFiltered['u'],aveDataFiltered['v'])
    plt.title(title)
    plt.imshow(im,alpha=.5)

baseFilePath = '/media/stian/Evan Dutch/Bifurcation/12805/05-02-2019/stitched/207/'
files = '(\d{4})_(\d{4}).txt'
frontFilePath = 'front/'
backFilePath = 'back/'
front_img_px = 1150
back_img_px = 230

frontData = readFiles(os.path.join(baseFilePath, frontFilePath), files)
backData = readFiles(os.path.join(baseFilePath, backFilePath), files)

# backFiles- cut off points after x
backData = backData[backData['x'] < (back_img_px + 640)]
# frontFiles- cur off points before x
frontData = frontData[frontData['x'] > (front_img_px - 690)]
frontData['x'] = frontData['x'] + (1280 - 640 - back_img_px)
# join dataframes
data = pd.concat([backData,frontData])
data['y'] = data['y'].max() - data['y'] + 15


vectorPlot(data, baseFilePath, baseFilePath[-4:-1])
centerSpeeds(data, baseFilePath[-4:-1])