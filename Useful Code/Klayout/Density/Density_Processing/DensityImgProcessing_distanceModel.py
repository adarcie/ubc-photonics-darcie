# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 13:53:30 2020

@author: Bigbo
"""
import numpy as np
from matplotlib import pyplot as plt

#define model for distance dependence from data
# - returns process bias amount
# - distance in um

def dist_model(d,params):
    peak_wl=params[0]+params[1]*np.log(params[2]*(d-params[3]))
    return peak_wl

def dist_conversion(d):
    max_distance=1000
    nmshift_per_nmbias=1.3
    
    params=[1.5170,   0.0021,    7.3313,   -0.4852]
    peak_wl=dist_model(d,params)
    peak_wl_max=dist_model(max_distance,params)
    return (peak_wl_max-peak_wl)/nmshift_per_nmbias

def distance_contribution(grid_dx,grid_dy,ETCH_WIDTH,ETCH_LENGTH):
    
    d_offset=0
    
    #use center point of each grid point for calculation
    grid_points_x=np.arange(d_offset,ETCH_WIDTH,grid_dx)+grid_dx/2 
    grid_points_y=np.arange(-ETCH_LENGTH/2,ETCH_LENGTH/2,grid_dy)+grid_dy/2
    
    grid_matrix=np.zeros((len(grid_points_y),len(grid_points_x)))
    distance_list=[]
    bias_list=[]
    
    BIAS_SUM=0
    
    for i in range(len(grid_points_x)):
        x=grid_points_x[i]
        for j in range(len(grid_points_y)):
            y=grid_points_y[j]
            
            dist=np.sqrt(x**2+y**2)
            bias=dist_conversion(dist)
            #set limit where small values become 0
            if bias<dist_conversion(d_offset)/100:
                bias=0
            BIAS_SUM=BIAS_SUM+bias
            grid_matrix[j,i]=bias
            
            distance_list.append(dist)
            bias_list.append(bias)
            
            
    bias_contributions=grid_matrix/BIAS_SUM
    print(sum(sum(bias_contributions)))
    
    #plot contribution from every point in grid
    plt.imshow(bias_contributions, 
               interpolation='nearest',extent=[min(grid_points_x)-grid_dx/2,
                                              max(grid_points_x)+grid_dx/2,
                                              min(grid_points_y)-grid_dy/2,
                                              max(grid_points_y)+grid_dy/2])
    plt.colorbar()
    plt.title("Spatial Bias Contribution")
    plt.show()
    
    #plot effective distance ratio vs distance
    bias_list=bias_list/BIAS_SUM #normalize bias_list
    plt.plot(distance_list,bias_list)
    plt.title("Distance Contribution Ratio")
    plt.ylabel("Contribution Ratio")
    plt.show("Distance")
    
    return distance_list,bias_list,BIAS_SUM

## correct inital calibration based on total bias amount
def dist_conversion_corrected(d,bias_list,distance_list):
    #find closest distance value
    closest_ind=min(range(len(distance_list)), key=lambda i: abs(distance_list[i]-d))
    
    return bias_list[closest_ind]


#plot distance model - UNCORRECTED
dist=np.linspace(0,1000)
shifts=dist_conversion(dist)
plt.plot(dist,shifts)
plt.title("Bias Distance Model")
plt.xlabel("Distance (um)")
plt.ylabel("Bias Shift (nm)")
plt.show()


### Sum Chunks in bulk etched area and normalize to find influence from a given chunk
# - see how well the effect per grid point converges by plotting sum
bias_sums=[]
GRID_SIZES=np.linspace(10,100,10)
grid_dx=100
grid_dy=100



for GRID_SIZE in GRID_SIZES:
    
    ETCH_WIDTH=grid_dx*GRID_SIZE
    ETCH_LENGTH=grid_dy*(GRID_SIZE+1)

    [distance_list,bias_list,BIAS_SUM]=distance_contribution(grid_dx,grid_dy,ETCH_WIDTH,ETCH_LENGTH)
    bias_sums.append(BIAS_SUM)
    
            
plt.title("Convergence Test")
plt.ylabel("BIAS_SUM")
plt.xlabel("GRID_SIZE")
plt.plot(GRID_SIZES,bias_sums)
plt.show()


#show extraction for one value given a distance
ETCH_WIDTH=grid_dx*GRID_SIZE
ETCH_LENGTH=grid_dy*(GRID_SIZE+1)

print(dist_conversion_corrected(25,bias_list,distance_list))



        
        
        
        
        
        
        
        
        
        