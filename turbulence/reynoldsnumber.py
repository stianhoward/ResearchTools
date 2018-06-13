# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 12:57:19 2017

@author: edutc
"""
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt


# Program to calculate the reynolds number of 8CB as a function of velocity
def ReynoldsNumber(v):
    '''A function that calculates the reynolds number of 8CB as a function of velocity
       
       Parameters
       ----------
       v: velocity in m/s
       
       Returns
       -------
       Re: Reynolds Number'''
       
    visc  = 0.052                #vescocity of 8CB in Pa s
    L     = 0.003556             #width of channel in m
    L     = 0.00245
    pd    = 1000.0               #density of 8CB in kg m^-3
    Re = v*L*pd/visc
    return Re 

'''
data=pd.read_csv('C:\\Users\\edutc\\Desktop\\WORK\\racetrack\\data.csv')    #read in racetrack data

data=data/1000

velocity = np.array(data['Velocity'])
ReynoldVals=ReynoldsNumber(velocity)
plt.scatter(velocity,ReynoldVals)
plt.xlabel('velocity (m/s)')
plt.ylabel('Re')


print('In the racetrack experiment, the reynolds number ranged from {:.5f} to {:.5f}'.format(ReynoldVals.min(),ReynoldVals.max()))
'''
