# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np

filename="myfile"

file1=open(filename+".txt")
lines=file1.readlines()
file1.close()

#print(lines)
lines=lines[0]

#get width and height of matrix (number of blocks)
width=lines.split("width=")[1]
width=int(width.split(";")[0])

height=lines.split("height=")[1]
height=int(height.split(";")[0])

#print(width,height)

##Get position data
#Ex. mono:matrix=(100,0,1585.58) (0,100,-904.316) (0,0,1);
positiondata=lines.split("(")
row1=positiondata[1].split(")")[0].split(',')
row2=positiondata[2].split(")")[0].split(',')
row3=positiondata[3].split(")")[0].split(',')

#print(row1,row2,row3)

tmatrix=[[row1[0],row1[1],row1[2]],
         [row2[0],row2[1],row2[2]],
         [row3[0],row3[1],row3[2]]]
tmatrix=np.array(tmatrix)
tmatrix=tmatrix.astype(np.float)

#print(tmatrix)

startx=tmatrix[0][2]
starty=tmatrix[1][2]

dx=tmatrix[0][0]
dy=tmatrix[1][1]

#create x,y arrays
x_list=np.zeros(width)
y_list=np.zeros(height)

#create arrays assuming center point is start
for i in range(width):
    x_list[i]=startx+i*dx
for i in range(height):
    y_list[i]=starty+i*dy
    
#correct arrays to start from bottom left (rather than center)
x_list=x_list-(max(x_list)-min(x_list))/2
y_list=y_list-(max(y_list)-min(y_list))/2

#print(x_list)
#print(y_list)

#extract density data (list form)
data=lines.split("data=[")[1]
data=data.split(";")[0:-1]

#print(data)

#apply image data to matrix
image_data=np.zeros((height,width))
ind=0
for i in range(height):
    for j in range(width):
        image_data[i,j]=float(data[ind])
        ind=ind+1



#### DATA to Export ####
#print(image_data)
#print(x_list,y_list)

#Export data to another text document
#fixed_filename=filename+"_fixed"
#file2=open(fixed_filename+".txt","w+")
#file2.write(image_data+"\n")
#file2.write(x_list+"\n")
#file2.write(y_list+"\n")
#file2.close()


## plot image data to check for accuracy
from matplotlib import pyplot as plt
plt.imshow(np.flip(image_data), interpolation='nearest')
plt.colorbar()
plt.title("Density Map")
plt.show()



######### PROCESSING ############


#function to define bias amounts
def get_bias_amount(Distance,ni,nj,image_data,R_max):
    
    #distance dependence (from 100% fill)
    B_dist=1-Distance/R_max#nm
    
    #100% close proximity bias
    B_100=100#nm/100%
    
    #density dependent bias
    bias_per_percent=-5#nm/%fill
    B_density=bias_per_percent*image_data[nj,ni]*100
    
    correction_bias=-B_dist*B_density/B_100
    return correction_bias

    


### Create array of bias values ###
bias_matrix=np.zeros((height,width))

R_max=500 #calibration value (what actually happens)

#determine approximate bounding for search region
min_dim=min([dx,dy])
max_dn=int(round(R_max/min_dim))
print(min_dim,max_dn)


for i in range(width):#loop over all cells
    for j in range(height):
        
        #if image_data[j,i]>0:#make sure cell isn't empty (can remove if different layer)
            xi=x_list[i]
            yj=y_list[j]
            
            bias_amount=0
            #loop over AOE cells (for each cell)
            for ii in range(i-max_dn,i+max_dn+1):
                if ii>=0 and ii<=width-1:#make sure width is within bounds
                    for jj in range(j-max_dn,j+max_dn+1):
                        if jj>=0 and jj<=height-1:#make sure height is within bounds
                            dxi=(ii-i)*dx
                            dyj=(jj-j)*dy
                            R=(dxi**2+dyj**2)**0.5
                            if R<=R_max:
                                d_bias=get_bias_amount(R,ii,jj,image_data,R_max)
                                bias_amount=bias_amount+d_bias
            bias_matrix[j,i]=bias_amount
                                
                            
                            
plt.imshow(np.flip(bias_matrix), interpolation='nearest')
plt.colorbar()
plt.title("Correction Bias")
plt.show()
                
        
        
        
        