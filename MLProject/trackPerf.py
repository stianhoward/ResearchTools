import json
import trackpy as tp
tp.quiet(suppress=True)
import matplotlib.pyplot as plt
import numpy as np
import glob
import pandas as pd
import os

# Import data from JSON files into DataFrame
def loadJSON(directory,height):
  array = np.empty([0,3])
  files = sorted(glob.glob(os.path.join(directory,'*.json')))
  for j in range(0,len(files)):
    with open(files[j], 'r') as read_file:
      data = json.load(read_file)
      for i in range(0,len(data)):
        x = (data[i]['bottomright']['x'] + data[i]['topleft']['x'])/2
        y = (data[i]['bottomright']['y'] + data[i]['topleft']['y'])/2
        #y = height-(data[i]['bottomright']['y'] + data[i]['topleft']['y'])/2
        array = np.vstack([array,[j,x,y]])

  array = array.astype(int)
  dataset = pd.DataFrame({'frame':array[:,0],'x':array[:,1],'y':array[:,2]})
  return dataset

# Import data from CSV files into DataFrame
def loadCSV(directory,height):
  files = sorted(glob.glob(os.path.join(directory,'*.dat')))
  array = np.empty([0,3])
  for fileName in files:
    tmp = np.loadtxt(fileName, delimiter=' ')
    frame = os.path.basename(fileName).split('.')[0].split('_')[-1] 
    if tmp.size == 3:
      array = np.vstack([array,[frame,tmp[1],tmp[2]]])
    else:
      tmp[:,0] = frame
      array = np.vstack([array,tmp])
  array = array.astype(float).astype(int)
  #array[:,2] = height - array[:,2]
  dataset = pd.DataFrame({'frame':array[:,0],'x':array[:,1],'y':array[:,2]})
  return dataset

# Plot humand data as crosses and ML data as track on an image  
def plotTracks(humanData,mlTracks,imgPath):
  plt.imshow(plt.imread(imgPath),cmap='gray')
  for particle in mlTracks['particle'].unique():
    path = mlTracks[mlTracks.particle == particle]
    plt.plot(path.x,path.y,'b-')
  plt.plot(humanData.x,humanData.y,'rx')

# Simply link the objects between frames with trackpy
def trackPoints(data):
  t = tp.link_df(data, 15, memory = 10)
  t1 = tp.filter_stubs(t,70)
  return t1

# Return the shortest distance between and point and a set of points
def pointDist(point,array):
  min_dist = np.sqrt((array.x-point.x)**2 + (array.y-point.y)**2)
  #dist = math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
  return(min_dist.min())
  
# Calculate the RMS of the distances between points and the nearest track
def calcError(human,ml):
  dists = np.empty(shape = (0))
  human = human[['x','y']]
  for i in range(0,len(human.index)):
    min_dist = [pointDist(human.loc[i,:],ml[['x','y']])] 
    dists = np.append(dists,min_dist)
  rms = np.sqrt(np.mean(dists ** 2)) 
  plt.title('RMS: ' + str(rms))
  print(rms)

def trackRMSplot():
  humanSet = loadCSV('/home/stian/Desktop/testVid/highC-r1/CSV',512)
  mlSet = loadJSON('/home/stian/Desktop/testVid/highC-r1/outIMG/',512)
  tracks = trackPoints(mlSet)
  plotTracks(humanSet,tracks,'/home/stian/Desktop/testVid/highC-r1/2019-06-28_r1_0300.tif')
  calcError(humanSet,mlSet)
  plt.savefig('/home/stian/Desktop/testVid/highC-r1/track.jpg')
  plt.show()

def pointPlot():
  mlSet1 = loadJSON('/media/stian/StianHD/tmp/images-cent/outIMG',800)
  mlSet2 = loadJSON('/media/stian/StianHD/tmp/images-off/outIMG',800)
  missingPoints1 = [14,40,41,42,43,44,79,105,106,131,132,157,158,184,187,210,211,236,237,238,263,264,289,316,320,343,368,398,420,421,423,455,456,457,458,459,460,461,484,485,486]*int(800/500)
  missingPoints2 = [1,6,7,8,10,15,17,18,22,45,54,56,79,80,81,184,245,265,290,291,318,343,370,397,398,467,471,472,475,486,487,488] * int(800/500)
  plt.plot(mlSet1.x,mlSet1.y,'b.')
  plt.plot(mlSet2.x,mlSet2.y,'b.')
  plt.plot(missingPoints1,missingPoints1,'rX')
  ys = [int(i)+40 for i in missingPoints2]
  plt.plot(missingPoints2,ys,'rX')
  plt.axis([0,800,0,800])
  plt.grid(b=True)
  plt.show()

if __name__ == "__main__":
  pointPlot()
