import json
import trackpy
import matplotlib.pyplot as plt
import numpy as np
import glob
import pandas as pd
import os

def loadJSON(directory):
  array = np.empty([0,3])
  files = sorted(glob.glob(os.path.join(directory,'*.json')))
  for j in range(0,len(files)):
    with open(files[j], 'r') as read_file:
      data = json.load(read_file)
      for i in range(o,len(data)):
        x = (data[i]['bottomright']['x'] + data[i]['topleft']['x'])/2
        y = (data[i]['bottomright']['y'] + data[i]['topleft']['y'])/2
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
  
def plotXs(data):
  plt.plot(data.x,data.y,'rx')

if __name__ == "__main__":
  humanSet = loadCSV('/home/stian/Desktop/validation/highC/annotations/csv/')
  mlSet = loadJSON('/home/stian/Dekstop/validation/highC/Pos0/corrected')
  plotXs(humanSet)
  plt.show()
