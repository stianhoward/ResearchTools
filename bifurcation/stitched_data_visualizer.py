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

    data.loc[:,'x'] = data['x'].map(lambda x: custom_round(x, base))
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
    plt.figure()
    plt.plot(x,velocities)
    plt.title(title)
    

def vectorPlot(data, imagePath, filter = 400, title = 'VectorPlot', plot = 1):
    # Import background image
    os.chdir(imagePath)
    im = mpl.image.imread(glob.glob('*.bmp')[0])

    # Sort the data
    data = data[data['filtered']==0]

    groups = data.groupby(['x','y'])
    aveData = groups.agg('mean')
    vel = aveData['u']**2+aveData['v']**2
    valueVel = vel[~vel.isnull()]
    valueVel=valueVel[np.abs(valueVel)<filter]
    keys = valueVel.keys()

    # Plot the data
    plt.figure()
    aveDataFiltered=aveData.loc[keys]
    plt.quiver(aveDataFiltered.index.get_level_values(0),aveDataFiltered.index.get_level_values(1),aveDataFiltered['u'],aveDataFiltered['v'])
    plt.title(title + ' Filter: ' + str(filter), fontsize = 20)
    plt.imshow(im,alpha=.5)


def vertSlices(data, saveBasePath, title= "Verticle Slices"):
    # Check if the save path exists, and create if it doesn't
    if not os.path.isdir(saveBasePath):
        if not os.path.isdir(os.path.split(saveBasePath)[0]):
            os.mkdir(os.path.split(saveBasePath)[0])
        os.mkdir(saveBasePath)
    
    data = data.copy()
    # Function used in setting bin widths
    def custom_round(x, base=20):
        return int(base * round(x/base)) 
    
    # Sort the data
    data = data[data['filtered']==0]

    # Set data to 35 pixel chunks
    base = 100

    data.loc[:,'x'] = data['x'].map(lambda x: custom_round(x, base))
    data.loc[:,'y'] = data['y'].map(lambda y: custom_round(y,base/5))

    # Organize the data by x and y, averaging velocities
    data = data.groupby(['y','x']).mean()
    data = data.reset_index()
    data = data.fillna(0)

    # set scale for x-positions to plot
    max = data['x'].max()
    topColumn = int(max/base) - 1

    
    # Determining the max velocity for balancing the velocity scale
    tmpData = data[data.x <= topColumn*base]
    tmpData = tmpData[tmpData.x >= 2*base]
    tmpData = tmpData[tmpData.x < (topColumn * base)]
    velocities = np.sqrt(np.square(tmpData['u'])  + np.square(tmpData['v']))
    maxV = velocities.max()
    print(maxV)    

    plt.figure(figsize=(20,10))
    for i in range(2,topColumn):	
        xPos = i * base
        
        # Create the x and velocity arrays
        xs = data[data['x'] == xPos]
        ys = xs['y']
        velocities = np.sqrt(np.square(xs['u'])  + np.square(xs['v']))
        velocities = velocities * np.sign(xs['u']) * base / maxV 

        '''
        y_selected = data[data['y'] == 400]
        x = y_selected['x']
        velocities = np.sqrt(np.square(y_selected['u'])  + np.square(y_selected['v']))
        '''
        velocities = xPos + velocities 
        # Plot the data
        plt.plot(velocities, ys)
    
    titler = title + ' ' + os.path.split(saveBasePath)[1]
    plt.title(titler)
    plt.savefig(os.path.join(os.path.split(saveBasePath)[0], os.path.split(saveBasePath)[1] +'.png'))
    plt.close()
    #plt.show()
        
        
def process(baseFilePath):
    savePath = os.path.join(os.path.split(os.path.split(baseFilePath)[0])[0] + '/analysis/xslices' , os.path.split(baseFilePath)[1])

    files = '(\d{4})_(\d{4}).txt'
    frontFilePath = None
    backFilePath = 'back/'
    front_img_px = 1150
    back_img_px = 230


    if (frontFilePath and backFilePath):
        frontData = readFiles(os.path.join(baseFilePath, frontFilePath), files)
        backData = readFiles(os.path.join(baseFilePath, backFilePath), files)

        # backFiles- cut off points after x
        backData = backData[backData['x'] < (back_img_px + 640)]
        # frontFiles- cur off points before x
        frontData = frontData[frontData['x'] > (front_img_px - 740)]
        frontData['x'] = frontData['x'] + (1280 - 590 - back_img_px)
        # join dataframes
        data = pd.concat([backData,frontData])
        data['y'] = data['y'].max() - data['y'] + 15
    elif frontFilePath:
        pass
    elif backFilePath:
        backData = readFiles(os.path.join(baseFilePath, backFilePath), files)
        data = backData


    #vectorPlot(data, baseFilePath, 10, 'Flow: ' + baseFilePath[-5:-1] + 'V')
    #vectorPlot(data, baseFilePath, 400, 'Flow: ' + baseFilePath[-5:-1] + 'V')
    #centerSpeeds(data, 'Flow: ' + baseFilePath[-4:-1] + 'V')
    vertSlices(data, savePath, 'Sm A MX12160: Vertical Slices')
    #surfacePlot(data, 'Flow: ' + baseFilePath[-4:-1] + 'V')
    #plt.show()


FilePaths = ['/media/stian/Evan Dutch/Bifurcation/12160/DataSet2/stitched/215',
'/media/stian/Evan Dutch/Bifurcation/12160/DataSet2/stitched/225',
'/media/stian/Evan Dutch/Bifurcation/12160/DataSet2/stitched/235',
'/media/stian/Evan Dutch/Bifurcation/12160/DataSet2/stitched/245',
'/media/stian/Evan Dutch/Bifurcation/12160/DataSet2/stitched/255',
'/media/stian/Evan Dutch/Bifurcation/12160/DataSet2/stitched/265',
'/media/stian/Evan Dutch/Bifurcation/12160/DataSet2/stitched/275',
'/media/stian/Evan Dutch/Bifurcation/12160/DataSet2/stitched/285',
'/media/stian/Evan Dutch/Bifurcation/12160/DataSet2/stitched/295']

'''
FilePaths = ['/media/stian/Evan Dutch/Bifurcation/12805/DataSet3/stitched/215',
'/media/stian/Evan Dutch/Bifurcation/12805/DataSet3/stitched/225',
'/media/stian/Evan Dutch/Bifurcation/12805/DataSet3/stitched/235',
'/media/stian/Evan Dutch/Bifurcation/12805/DataSet3/stitched/245',
'/media/stian/Evan Dutch/Bifurcation/12805/DataSet3/stitched/255',
'/media/stian/Evan Dutch/Bifurcation/12805/DataSet3/stitched/265',
'/media/stian/Evan Dutch/Bifurcation/12805/DataSet3/stitched/275',
'/media/stian/Evan Dutch/Bifurcation/12805/DataSet3/stitched/285']
'''


for Path in FilePaths:
    process(Path)
