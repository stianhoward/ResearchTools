'''
    Script for importing csv file produced from turb.py, and tracking individual particles
    in specific selectrion of frames/ areas of a scene. 

    Goals:
    - Inputs
        - Import csv files of relevance
        - Request frames desired. 
            - determine through request, hard code, interactive, config file, etc.
        - Hard code relevant region. 
            - Potentially make this requested, but better to default to hard code as relatively consistent range
    - Processing
        - Limit to particle size/ mass in order to limit too much. Might need added turb.py parameter and re-process
        - Track movement of particle frame by frame, and store path
    - Output
        - Output image file consisting of the path the particle follows
        - Dialog asking where to save it? Or hard code? --> probably more likely in the plots folder already put in place.

'''

from tkinter import filedialog, Tk
#from tkinter import *
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import glob
import sys
import os


# Constants
FRAME_MIN = 10
FRAME_MAX = 600
X_MIN = 450
X_MAX = 650
Y_MIN = 350
Y_MAX = 550


def main():
    single_tracking()


def single_tracking(save = True):
    # Inputs
    data_path = request_file_path("Select CSV file to open", os.path.expanduser('~'), (("CSV files","*.csv"),("all files","*.*")))
    end_image = load_image(data_path,FRAME_MAX)
    
    # Operations
    figure = particle_tracking(data_path,end_image)
    if save:
        save_path = request_save_loc(data_path)
        save_figure(figure, save_path)
        plt.close()
    else:
        return figure


def request_file_path(win_name="Select a file", start_dir = '/', file_types = ("all files","*.*"), abort = True):
    # Create window instance, and hide it then ask for the directory
    try:
        root = Tk()
        root.withdraw()
        path = filedialog.askopenfilename(title = win_name, initialdir= start_dir, filetypes = file_types)
        root.destroy()
    except:
        print("Failed to request file path", sys.exc_info())
        quit()
    if abort and path == ():
        print("No path selected - Aborting")
        quit()

    if not os.path.isfile(path):
        print("Path does not point to accessible file - Aborting")
        quit()
    
    return path


def load_image(data_path,end_frame):
    image_path = request_file_path("Select frame " + str(end_frame), os.path.dirname(data_path), (("Bitmap files","*.bmp"),("all files","*.*")))
    if not os.path.isfile(image_path):
        images = glob.glob(os.path.join(image_path,"*",end_frame,".bmp"))
        images.sort()
        if not images:
            print("No image found in selected directory - Aborting")
            quit()
        else:
            image_path = images[0] 
    try:
        return mpl.image.imread(image_path)
    except:
        print("Unexpected error importing found image file: ", sys.exc_info())
        return None


def particle_tracking(data_path, end_image):
    raw_data = import_data(data_path)
    data = process_data(raw_data)
    figure = create_image(data,end_image)
    return figure


def import_data(path):
    try:
        raw_data = pd.read_csv(path)
    except:
        print("Failed to import CSV file", sys.exc_info())

    return raw_data


def process_data(raw_data):
    raw_data = raw_data.astype({'x':'float','y':'float','frame':'int','particle':'int'})
    data = raw_data.loc[:,['x','y','frame','particle']]
    data = data[data['frame'].between(FRAME_MIN, FRAME_MAX) & data['x'].between(X_MIN, X_MAX) & data['y'].between(Y_MIN, Y_MAX)]
    data.groupby(['particle','frame']).mean()
    if data.empty:
        print("Data in bounds is empty - Aborting")
        quit()
    else:
        return data


def create_image(data, image, title=''):
    particles = np.unique(data.reset_index()['particle'])
    data = data.groupby(['particle','x','y']).mean()
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plt.imshow(image)
    # plt.imshow(image[Y_MIN:Y_MAX,X_MIN:X_MAX])
    for particle in particles:
        ax1.plot(data.loc[particle].reset_index()['x'], data.loc[particle].reset_index()['y'], label = particle)
    plt.legend(loc='upper left')
    plt.ylabel('y (pixels)')
    plt.xlabel('x (pixels)')
    plt.title(title)
    return fig


def request_save_loc(data_path = os.path.expanduser('~')):
    try:
        root = Tk()
        root.withdraw()
        path =  filedialog.asksaveasfilename(initialdir = os.path.dirname(data_path),title = "Save image as...",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
        root.destroy()
    except:
        print("Failed to request file path", sys.exc_info())
        quit()

    print(path)
    if os.path.exists(os.path.dirname(path)):
        return path
    else:
        try:
            os.makedirs(os.path.dirname(path))
        except:
            print("No valid path selected and/or path creation failed - Aborting")
            quit()


def save_figure(fig, save_path = ''):
    if save_path == '':
        save_path = request_save_loc()
    try:
        plt.savefig(os.path.join(save_path))
    except:
        print("Unexpected error saving plot:", sys.exc_info())


if __name__ == '__main__':
    main()