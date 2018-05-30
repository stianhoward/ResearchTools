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
import glob
import sys
import os
FRAME_RATE= 8000        # FrameRate
PIXEL_SIZE=.0044        # mm per pixel

# base_path = '/media/stian/Evan Dutch/Turbulence/2018-05-21/'
base_path = '/home/stian/Desktop/test/'

def main(base_path):
    # locate films in the path
    films = glob.glob(base_path + 'Film[1-9]')
    for film in films:
        film = film + '/'
        valuematrices = glob.glob(film + 't[1-9]valuematrix.csv')
        for matrix in valuematrices:
            open_path = matrix
            save_path = film + 'plots/'
            save_name = matrix.strip()[-16] + '.png'

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            try:
                # Import a data set
                raw_data = pd.read_csv(open_path)
                # Import extra info about data set                   
                location = load_location(film + matrix.strip()[-16] + '/position.txt')
                # Create and save Scatter plot of data
                scatter(raw_data, location, save_path, save_name)
                vector(raw_data, location, save_path, save_name, film)
            except:
                print("Unexpected error:", sys.exc_info())
                print("Failed to open and process data for: " + open_path)



def load_location(filePath):
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
    plt.title(location + ': \nVelocity vs. Position',fontsize=20)
    ax.legend()
    try:
        fig.savefig(save_path + 'scatter' + save_name)
    except:
        print("Unexpected error saving scatter plot:", sys.exc_info())
    plt.close()


# Function used in setting bin widths
def custom_round(x, base=20):
    return int(base * round(float(x)/base)) 


def vector(raw_data, title, save_path, save_name, film_dir):
    # Import image and data
    img = retrieve_image(film_dir + save_name[0])
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
        quiver_plot(data, title, save_path + 'vectorplot_overlay' + save_name, img)
    quiver_plot(data, title, save_path + 'vectorplot' + save_name, None)


def retrieve_image(image_directory):
    # Path to 4th object in scene directory. When naming finalized, change to more reliable method.
    first_file = image_directory + '/' + os.listdir(image_directory)[4] 
    print('Using image: ' + first_file)
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
    ticks_y = mpl.ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x * PIXEL_SIZE))
    ax.yaxis.set_major_formatter(ticks_y)

    # Save Plot
    try:
        plt.savefig(save_path)
    except:
        print("Unexpected error saving vector plot:", sys.exc_info())
    plt.close()


if __name__ == '__main__':
    main(base_path)