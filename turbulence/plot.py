'''
Script for plotting data for particle movements.
This script inports the data, exported by turb.py in 
.csv format, and displays the data in a usable format.

USE:
- Call the plot.main(base_path) function from another script
- Simply run this script itself, editing the base_path argument below

base_path is the path to the folder containing multiple films using 
the labs normal file structure.
'''

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import glob
import sys
import os

FRAME_RATE= 7955        # FrameRate
PIXEL_SIZE=.0044        # mm per pixel

base_path = '/media/stian/Evan Dutch/Turbulence/2018-05-25/'
# base_path = '/home/stian/Desktop/2018-05-23/'

def main(base_path):
    cross_flow(base_path)
    # locate films in the path
    films = glob.glob(os.path.join(base_path, 'Film[1-9]'))
    for film in films:
        valuematrices = glob.glob(os.path.join(film, 't[1-9]valuematrix.csv'))
        for matrix in valuematrices:
            open_path = matrix
            save_path = os.path.join(film, 'plots')
            save_name = matrix.strip()[-16] + '.png'

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # Import a data set
            try:
                raw_data = pd.read_csv(open_path)
            except:
                print("Unexpected error:", sys.exc_info())
                print("Failed to open and process data for: " + open_path)
            
            # Import extra info about data set                   
            location = load_location(os.path.join(film, matrix.strip()[-16], 'position.txt'))
            # Create and save Scatter plot of data
            scatter(raw_data, location, save_path, save_name)
            vector_plot(raw_data, location, save_path, save_name, film)


def load_location(filePath):
    #Try to open info about file location in 'position.txt'
    try:
        file = open(filePath)
        location = file.read()
        location = location.strip()
        file.close()
    except:
        location = None
        # Todo: Collect all of these to print at the end under one print.
        print("No 'position.txt' file found in: " + filePath)

    return location

# Code from old scripts. Bad representation of data- mostly untouched
def scatter(raw_data, location, save_path, save_name):
    yslice1 = raw_data.astype({'x':'int','y':'int'})    # set x and y values to integers

    yslice1['x']=yslice1['x'].apply(lambda x: custom_round(x, base=10))
    ygrouped1=yslice1.groupby(['x'],as_index=False).agg({'dr':['mean','std']})
    ygrouped1.columns=['x','dr','std']
    y1=ygrouped1.fillna(0)                              # replace NaNs with 0's

    x1=(-210+y1['x'])*PIXEL_SIZE                        # Determin where the '210' value comes from. Potentially offset? half of width?
    dr1=y1['dr']*FRAME_RATE*PIXEL_SIZE      

    fig=plt.figure()
    ax=fig.add_subplot(111)

    ax.scatter(x1,dr1,color='r',label='0.31750 SLPM')

    plt.xlabel('Position',fontsize=20)
    plt.ylabel('Velocity (mm/s)',fontsize=20)
    if location == None:
        location = ''
    plt.title(location + ': \nVelocity vs. Position',fontsize=20)
    ax.legend()
    try:
        fig.savefig(os.path.join(save_path, 'scatter' + save_name))
    except:
        print("Unexpected error saving scatter plot:", sys.exc_info())
    plt.close()


# Function used in setting bin widths
def custom_round(x, base=20):
    return int(base * round(float(x)/base)) 


def vector_plot(raw_data, title, save_path, save_name, film_dir):
    # Import image and data
    img = retrieve_image(os.path.join(film_dir, save_name[0]))
    raw_data = raw_data.astype({'x':'int','y':'int','dx':'float','dy':'float'})

    # Extract relevent parts of imported data
    data = raw_data.loc[:,['x','y','dx','dy']]

   # Set data to 50 pixel chunks
    data['x'] = data['x'].apply(lambda x: custom_round(x, base = 50))
    data['y'] = data['y'].apply(lambda y: custom_round(y, base = 50))

    # Organize the data by x and y, averaging velocities
    data = data.groupby(['x','y']).mean()
    data = data.reset_index()
    data.dy = data.dy * -1

    # These need to be in this order since data is sent by referene, and edits are made in the display process.
    # Potential fix is to change dy and y direction in the call for plt.quiver itself, or assign data.y to a new variable in quiver_plot()
    if img is not None:                                                 # Call quiver_plot to actually perform the plotting
        quiver_plot(data, title, os.path.join(save_path, 'vectorplot_overlay' + save_name), img)
    quiver_plot(data, title, os.path.join(save_path , 'vectorplot' + save_name), None)


def retrieve_image(image_directory):
    # Path to 4th object in scene directory. When naming finalized, change to more reliable method.
    first_file = image_directory + '/' + os.listdir(image_directory)[4] 
    # print('Using image: ' + first_file)
    try:
        return mpl.image.imread(first_file)
    except:
        print("Unexpected error importing found image file: ", sys.exc_info())
        return None


def quiver_plot(data, title, save_path, img):
    # Plotting
    fig = plt.figure(figsize=(12,10))
    ax = fig.add_subplot(111)
    if img is not None:
        # If an image is input, plot that first
        plt.imshow(img)
    else:
        # If no image, indexing start bottom left, so reverse y values
        data.y = data.y * -1
    plt.quiver(data['x'],data['y'],data['dx'],data['dy'], color='red')
    
    # Labels and title
    plt.title(title, fontsize = 45)
    plt.xlabel('x-distance (mm)', fontsize = 30)
    plt.ylabel('y-distance (mm)', fontsize = 30)

    # Adjust axes scaling
    ticks_x = mpl.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x * PIXEL_SIZE))
    ax.xaxis.set_major_formatter(ticks_x)
    #ticks_y = mpl.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x * PIXEL_SIZE))
    #ax.yaxis.set_major_formatter(ticks_y)

    # Save Plot
    try:
        plt.savefig(save_path)
    except:
        print("Unexpected error saving vector plot:", sys.exc_info())
    plt.close()


def load_paths(base_path, make_save_dir = True):
    paths = []
    # locate films in the path
    films = glob.glob(base_path + 'Film[1-9]')
    for film in films:
        film = film + '/'
        valuematrices = glob.glob(film + 't[1-9]valuematrix.csv')
        for matrix in valuematrices:
            paths.append(matrix)
            '''
            save_path = film + 'plots/'             #Should be in lower loop level???
            if not os.path.exists(save_path) and make_save_dir:
                os.makedirs(save_path)
            '''
    return paths


def save_figure(fig, save_path, name):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    try:
        plt.savefig(os.path.join(save_path, name))
    except:
        print("Unexpected error saving plot:", sys.exc_info())


def cross_flow(base_path):
    #Look into serparating by film...
    save_path = os.path.join(base_path, 'plots')
    paths = load_paths(base_path)
    # load in data and sort
    data = collect_data(paths)
    data = data.groupby(['y','source','x']).mean()
    # Serperate the data to plot
    ys = np.unique(data.reset_index()['y'].values)
    for y in ys:
        diagram = scatter_plot(data.loc[y],y)
        save_figure(diagram, save_path, str(y))
        plt.close()
        

def collect_data(paths):
    collected_data = pd.DataFrame()
    for path in paths:
        # Import a data set
        try:
            raw_data = pd.read_csv(path)
        except:
            print("Unexpected error inporting CSV:", sys.exc_info())

        # Extract relevent parts of imported data
        data = raw_data.loc[:,['x','y','dr']]

        # Set data to 50 pixel chunks
        data['x'] = data['x'].apply(lambda x: custom_round(x, base = 50))
        data['y'] = data['y'].apply(lambda y: custom_round(y, base = 50))

        # Organize the data by x and y, averaging velocities
        data = data.groupby(['x','y']).mean()
        data = data.reset_index()
        source = load_location(os.path.join(os.path.dirname(path), path.strip()[-16], 'position.txt'))
        if source == None:
            source = path.strip()[-16]
        sorted = pd.DataFrame({'source':source,'x':data.x,'y':data.y,'dr':data.dr})
        if collected_data.empty:
            collected_data = sorted
        else:
            collected_data = pd.concat([collected_data, sorted])
    return collected_data


def scatter_plot(data,title):
    sources = np.unique(data.reset_index()['source'])

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    for source in sources:
        ax1.scatter(data.loc[source].reset_index()['x'], data.loc[source].reset_index()['dr'].multiply(PIXEL_SIZE * FRAME_RATE), marker="o", label=source)
    plt.legend(loc='upper left')
    plt.ylabel('dr (mm/s)')
    plt.xlabel('position (pixels)')
    plt.title(title)
    return fig


if __name__ == '__main__':
    main(base_path)