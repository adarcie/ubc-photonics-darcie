import pya
import numpy as np


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

def layout_invert_resist_tone(self):

  
###################### GET DENSITY DATA #################################

  os.chdir("D:\\Nextcloud\\Useful Code\\Klayout\\Exports")
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
  print(image_data)
  print(x_list,y_list)

###################### PERFORM RESIZING #################################
  topcell = self
  layout = self.layout()

  p = pya.AbsoluteProgress("Biasing..")
  p.format_unit = 7

  # Create new layers
  layer_high = layout.layer(pya.LayerInfo(200, 0))
  layer_in=layout.layer(pya.LayerInfo(31,0))
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
  shapes_tile=cell.shapes(layer_tile)
  shapes_in=cell.shapes(layer_in)

  box_width=dx
  box_height=dy
  for x_ind in range(width):
    for y_ind in range(height):
      #center coord of each box
      x=x_list[x_ind]
      y=y_list[y_ind]
      
      density=image_data[y_ind][x_ind]
      
      ### CALIBRATION VALUE HERE ###
      db_dd=-0.23#nm shift per percent fill
      
      bias_nm=-db_dd*density*100
      
      #make sure no gaps in case of negative bias and no overlap for positive
      box_overlap=-bias_nm/1000
      dx=box_width+2*box_overlap
      dy=box_height+2*box_overlap
      
      
      #"place" region that will be re-sized
      cell.shapes(layer_tile).insert(pya.Box((x-dx/2)/dbu, (y-dy/2)/dbu, (x+dx/2)/dbu, (y+dy/2)/dbu))
          
      # perform sizing operations:  http://www.klayout.de/doc-qt4/code/class_Polygon.html
    
    
      #create temp shape along layer_in only where it is within layer_tile
      pya.ShapeProcessor().boolean(layout,cell,layer_tile,layout,topcell,layer_in,shapes_temp,pya.EdgeProcessor.ModeAnd,True,True,True)
      p.inc
    
      #compute local pattern density
      #area = shapes_temp.area()
      
      #bias layer_temp onto shapes_high
      pya.ShapeProcessor().size(layout,cell,layer_temp,shapes_temp,bias_nm,pya.EdgeProcessor.ModeOr,True,True,True)
      p.inc
      
      #move contents of layer_temp onto layer_high to be saved
      shapes_high.insert(shapes_temp)
      
      
      #remove temporary shapes
      shapes_tile.clear()
      
    
    
  topcell.insert(pya.CellInstArray(cell.cell_index(), pya.Trans(0, 0)))
  p.destroy
  
  
  
  
  
  
  
  

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
