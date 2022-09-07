
# Enter your Python code here

from pya import *
  
# Import functions from SiEPIC-Tools, and get technology details
from SiEPIC.utils import select_paths, get_layout_variables
TECHNOLOGY, lv, ly, cell = get_layout_variables()
dbu = ly.dbu
from SiEPIC.extend import to_itype
from SiEPIC.scripts import path_to_waveguide
import glob,os



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

  topcell = self
  layout = self.layout()
  
  TECHNOLOGY, lv, ly, cell = get_layout_variables()
  TextLayerN = cell.layout().layer(TECHNOLOGY['Text'])


  p = pya.AbsoluteProgress("Layout invert resist tone")
  p.format_unit = 7

  # Create new layers for the inverted layout: one high resolution, and one low resolution
  layer_high = layout.layer(pya.LayerInfo(103, 0))
  layer_in=layout.layer(pya.LayerInfo(1,0))
  layer_temp = layout.layer(pya.LayerInfo(300, 0))
  layer_tile = layout.layer(pya.LayerInfo(400, 0))
  
  
  # Create a new cell
  newcellname="text_labels_buffer1"
  delete_cell = layout.cell(newcellname)
  if delete_cell:
    layout.delete_cell(delete_cell.cell_index())
  text_cell = layout.create_cell(newcellname)
  
  
  
  # set up vertical array of buffer distances (um)
  yspacing=227
  #18 rows
  buffer_list=[2.5,3,3.5,4,4.5,5,5.5,6]#,10]#,15]#,20]#,]
  buffer_list=buffer_list#[::-1]
  density=0.15
  
  startx=0
  endx=100
  y_offset=50-12
  x_offset=65-40
  
  xlabel_orig=59.6+5.4-5.04
  ylabel_orig=178.5-1.5+0.766
  num_x_coords=1
    
    
  #create array of given device
  #cell_dev= ly.create_cell("PCM_Ring").cell_index()
#  cell_dev=layout.cell("Ring_Jaspreet").cell_index()
  cell_dev=layout.cell("Base_Ring").cell_index()
  #topcell.insert(pya.CellInstArray(

  tilingcells=[]
  for i in range(len(buffer_list)):
  
    # Create a new cell for each buffer size
    newcellname="tiling_buffer"+str(i)
    delete_cell = layout.cell(newcellname)
    if delete_cell:
      layout.delete_cell(delete_cell.cell_index())
    tilingcells.append(layout.create_cell(newcellname))
    tilingcell=tilingcells[i]
      
    for j in range(num_x_coords):
      t = pya.Trans(Trans.R0,(xlabel_orig+j*(endx-startx))/dbu, (ylabel_orig+i*yspacing)/dbu)
      text = pya.Text ("opt_in_TE_1550_device_reversed_dist_"+str(round(buffer_list[i]*1000))+"nm_col"+str(j)+"_norm", t)
      shape = text_cell.shapes(TextLayerN).insert(text)
      shape.text_size = 10*dbu
      t = Trans(Trans.R0, (x_offset+j*(endx-startx))/dbu, (y_offset+i*yspacing)/dbu)
      tilingcell.insert(CellInstArray(cell_dev, t))
    topcell.insert(pya.CellInstArray(text_cell.cell_index(), pya.Trans(0, 0)))

  #create tiling array
  for n in range(len(buffer_list)):
  
    
    tilingcell=tilingcells[n]
    print("Buffer:",str(buffer_list[n]))
    print(tilingcell)
    layer_tile = layout.layer(pya.LayerInfo(400, 0))
    
    mindistance=buffer_list[n]*1000#distance between pattern and nearest tiles (nm > 10)
    #make tiles

    density=density
    starty=n*yspacing
    endy=yspacing*(n+1)
  
    #fill per 100um box
    boxsize=1#um
    xsize=(density*boxsize**2)**0.5
    ysize=(density*boxsize**2)**0.5
    
    x=startx
    y=starty
    while x<endx:
      y=starty
      while y<endy:
        tilingcell.shapes(layer_tile).insert(pya.Box(x/dbu, y/dbu, (x+xsize)/dbu, (y+ysize)/dbu))
        y=y+boxsize
      x=x+boxsize

    


    # perform sizing operations:  http://www.klayout.de/doc-qt4/code/class_Polygon.html
    # 1000 nm
    shapes_high = tilingcell.shapes(layer_high)
    shapes_temp = tilingcell.shapes(layer_temp)
    shapes_tile=tilingcell.shapes(layer_tile)
    pya.ShapeProcessor().size(layout,tilingcell,layer_in,shapes_high,mindistance-10,pya.EdgeProcessor.ModeOr,True,True,True)
    p.inc
    pya.ShapeProcessor().size(layout,tilingcell,layer_high, shapes_temp, 10,pya.EdgeProcessor.ModeAnd,True,True,True)
    p.inc
    #shapes_high.clear()
    #pya.ShapeProcessor().boolean(layout,cell,layer_temp,layout,topcell,layer_in,shapes_high,pya.EdgeProcessor.ModeXor,True,True,True)
    pya.ShapeProcessor().boolean(layout,tilingcell,layer_tile,layout,tilingcell,layer_temp,shapes_tile,pya.EdgeProcessor.ModeANotB,True,True,True)
    layer_tile=layer_tile-layer_temp
    p.inc
    topcell.insert(pya.CellInstArray(tilingcell.cell_index(), pya.Trans(0, 0)))
    
  p.destroy
    


#run function


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
