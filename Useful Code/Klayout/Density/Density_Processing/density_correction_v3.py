import pya
import numpy as np
from datetime import datetime


'''
Resist types:

- Negative tone, e.g., HSQ
  Shapes drawn in the layout become silicon; everything else is etched
  Waveguide layer is thus the solid waveguide core
  
- Postive tone, e.g., ZEP, PMMA
  Shapes drawn in the layout get etched; everything else remains as silicon
  Waveguides drawn by creating trenches (cladding) rather than the core
  Less convenient for waveguides
  Excellent for photonic crystals (holes)
  
  OUT_MODE = # 1=one layer, 2=two layers
  
'''

#function to define bias amounts
def get_bias_amount(Distance,ni,nj,image_data,R_max):
    
    #distance dependence (from 100% fill)
    B_dist=1-Distance/R_max#nm
    ## NEED SOME FACTOR CORRESPONDING TO THE SIZE OF THE CHUNK
    
    #100% close proximity bias
    B_100=100#nm/100%
    
    #density dependent bias
    bias_per_percent=-0.3#nm/%fill
    B_density=bias_per_percent*image_data[nj,ni]*100
    
    correction_bias=-B_density#/B_100
    return correction_bias


def layout_invert_resist_tone(self):

  
###################### GET DENSITY DATA #################################
  print("Importing density data...")
  tic = datetime.now()
  os.chdir("D:\\Nextcloud\\Useful Code\\Klayout\\Density_Processing")
  filename="myfile"
  
  file1=open(filename+".txt")
  lines=file1.readlines()
  file1.close()
  
  lines=lines[0]
  
  ####get width and height of matrix (number of blocks)
  width=lines.split("width=")[1]
  width=int(width.split(";")[0])
  
  height=lines.split("height=")[1]
  height=int(height.split(";")[0])
  
  ####Get position data
  #Ex. mono:matrix=(100,0,1585.58) (0,100,-904.316) (0,0,1);
  positiondata=lines.split("(")
  row1=positiondata[1].split(")")[0].split(',')
  row2=positiondata[2].split(")")[0].split(',')
  row3=positiondata[3].split(")")[0].split(',')
  
  
  tmatrix=[[row1[0],row1[1],row1[2]],
           [row2[0],row2[1],row2[2]],
           [row3[0],row3[1],row3[2]]]
  tmatrix=np.array(tmatrix)
  tmatrix=tmatrix.astype(np.float)

  
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

  
  ####extract density data (list form)
  data=lines.split("data=[")[1]
  data=data.split(";")[0:-1]

  
  #map image data to matrix
  image_data=np.zeros((height,width))
  ind=0
  for i in range(height):
      for j in range(width):
          image_data[i,j]=float(data[ind])
          ind=ind+1
  
  
  
  #### DATA to Export ####
  #print(image_data)
  #print(x_list,y_list)
  toc = datetime.now()
  print(toc-tic)
  print("Density data imported."+"\n")
  
  
  
  #################### PROCESS DENSITY DATA TO GET RESIZE MATRIX ########
  ### Create array of bias values ###
  print("Creating biasing matrix...")
  tic = datetime.now()
  
  bias_matrix=np.zeros((height,width))
  
  R_max=10 #calibration value (what actually happens)
  
  #determine approximate bounding for search region
  min_dim=min([dx,dy])
  max_dn=int(round(R_max/min_dim))
  #print(min_dim,max_dn)
  
  
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
            
            
  toc = datetime.now()
  print(toc-tic)
  print("Biasing matrix completed."+"\n")
  

###################### PERFORM RESIZING #################################

  resize_layer=150
  target_layer=31
  print("Resizing layer "+str(target_layer)+" onto layer "+str(resize_layer)+"...")
  tic = datetime.now()
  
  topcell = self
  layout = self.layout()

  #setup progress bar
  p = pya.AbsoluteProgress("Biasing...")
  p.format_unit = 1
  p.unit = 1

  # Create new layers
  layer_high = layout.layer(pya.LayerInfo(resize_layer, 0))
  layer_in=layout.layer(pya.LayerInfo(target_layer,0))
  layer_temp = layout.layer(pya.LayerInfo(300, 0))
  layer_tile = layout.layer(pya.LayerInfo(400, 0))
  
  
  # Create a new cell
  newcellname="bias_tone"
  delete_cell = layout.cell(newcellname)
  if delete_cell:
    layout.delete_cell(delete_cell.cell_index())
  cell = layout.create_cell(newcellname)
  
    
  #define shapes based on layer
  shapes_high = cell.shapes(layer_high)
  shapes_temp = cell.shapes(layer_temp)
  shapes_tile = cell.shapes(layer_tile)
  shapes_in = cell.shapes(layer_in)

  box_width=dx
  box_height=dy
  progress=0
  
  for x_ind in range(width):
    for y_ind in range(height):
      
      #center coord of each box
      x=x_list[x_ind]
      y=y_list[y_ind]
      
      bias_val=bias_matrix[y_ind,x_ind]
      
      
      #make sure no gaps in case of negative bias and no overlap for positive
      box_overlap=-bias_val/1000
      dx=box_width+2*box_overlap
      dy=box_height+2*box_overlap
    
      #move region to different cell and make shapes from input layer
      step2start = datetime.now()
      
      clip_cell=layout.cell(layout.clip(layout.cell_by_name("top"),pya.Box((x-dx/2)/dbu, (y-dy/2)/dbu, (x+dx/2)/dbu, (y+dy/2)/dbu)))
      shapes_clipped=clip_cell.shapes(layer_in)
      
      step2end = datetime.now()
      step2=step2end-step2start
    
      
      #bias layer_temp onto layer_temp
      step3start = datetime.now()
      pya.ShapeProcessor().size(layout,clip_cell,layer_in,shapes_temp,bias_val,pya.EdgeProcessor.ModeOr,True,True,True)
      step3end= datetime.now()
      step3=step3end-step3start
      
      #print(bias_val)
      
      #delete temporary cell
      layout.prune_cell(clip_cell.cell_index(),20)
      
      #move contents of layer_temp onto layer_high to be saved
      step4start = datetime.now()
      shapes_high.insert(shapes_temp)
      step4end = datetime.now()
      step4=step4end-step4start
      
      #remove temporary shapes
      step5start = datetime.now()
      shapes_tile.clear()
      step5end = datetime.now()
      step5=step5end-step5start
      
      #update progress bar
      progress=progress+1
      p.set(progress/(width*height)*100,True)
      #print(step2,step3,step4,step5)
      
    
    
  topcell.insert(pya.CellInstArray(cell.cell_index(), pya.Trans(0, 0)))
  p.destroy
  
  toc = datetime.now()
  print(toc-tic)
  print("Layout finished! Correct layer: "+str(resize_layer)+"\n")
  
  
  
print("============ START ===========")

pya.Cell.layout_invert_resist_tone = layout_invert_resist_tone


lv = pya.Application.instance().main_window().current_view()
if lv == None:
  raise Exception("No view selected")
ly = lv.active_cellview().layout() 
if ly == None:
  raise Exception("No active layout")
cell = lv.active_cellview().cell
if cell == None:
  raise Exception("No active cell")


cell.layout_invert_resist_tone()
lv.add_missing_layers()
print("Done")

