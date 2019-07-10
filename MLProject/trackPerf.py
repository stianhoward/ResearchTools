import json
import trackpy as tp
import matplotlib.pyplot as plt
import numpy as np
import glob
import pandas as pd
import os

def loadJSON(directory,height):
  array = np.empty([0,3])
  files = sorted(glob.glob(os.path.join(directory,'*.json')))
  for j in range(0,len(files)):
    with open(files[j], 'r') as read_file:
      data = json.load(read_file)
      for i in range(0,len(data)):
        x = (data[i]['bottomright']['x'] + data[i]['topleft']['x'])/2
        y = height-(data[i]['bottomright']['y'] + data[i]['topleft']['y'])/2
        array = np.vstack([array,[j,x,y]])

  array = array.astype(int)
  dataset = pd.DataFrame({'frame':array[:,0],'x':array[:,1],'y':array[:,2]})
  return dataset

def loadCSV(directory):
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
  dataset = pd.DataFrame({'frame':array[:,0],'x':array[:,1],'y':array[:,2]})
  return dataset
  
def plotTracks(humanData,mlTracks):
  for particle in mlTracks['particle'].unique():
    path = mlTracks[mlTracks.particle == particle]
    plt.plot(path.x,path.y,'b-')
  plt.plot(humanData.x,humanData.y,'rx')

def trackPoints(data):
  t = tp.link_df(data, 15, memory = 10)
  t1 = tp.filter_stubs(t,70)
  return t1

def pointDist(point,array):
  min_dist = np.sqrt((array.x-point.x)**2 + (array.y-point.y)**2)
  #dist = math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
  return(min_dist.min())
  
def calcError(human,ml):
  dists = np.empty([1])
  human = human[['x','y']]
  for i in range(0,len(human.index)):
    dists = np.append(dists,[pointDist(human.loc[i,:],ml[['x','y']])])
  print(np.sqrt(np.mean(dists ** 2)))

if __name__ == "__main__":
  humanSet = loadCSV('/home/stian/Desktop/testVid/r2/MLCSV')
  mlSet = loadJSON('/home/stian/Desktop/outIMG/',800)
  tracks = trackPoints(mlSet)
  plotTracks(humanSet,tracks)
  calcError(humanSet,mlSet)
  plt.show()
