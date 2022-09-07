
# Enter your Python code here

import pya
from SiEPIC.utils import select_paths, get_layout_variables
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

  topcell = self
  layout = self.layout()
  
  TECHNOLOGY, lv, ly, cell = get_layout_variables()
  TextLayerN = cell.layout().layer(TECHNOLOGY['Text'])


  p = pya.AbsoluteProgress("Layout invert resist tone")
  p.format_unit = 7

  # Create new layers for the inverted layout: one high resolution, and one low resolution
  layer_high = layout.layer(pya.LayerInfo(102, 0))
  layer_in=layout.layer(pya.LayerInfo(31,0))
  layer_temp = layout.layer(pya.LayerInfo(300, 0))


  
  layer_tile = layout.layer(pya.LayerInfo(400, 0))
  
  
  # set up vertical array of biases
  yspacing=227
  #bias_list=[10, 20, 30, 60]
  bias_list=np.linspace(-30,10,9)
  
  startx=0
  endx=100
  y_offset=50
  x_offset=65
  
  xlabel_orig=27.33+0.35-0.06-27.52-0.1
  ylabel_orig=114.7-1.72-0.04+13.92+0.153
    
    
  #create array of given device
  #cell_dev= ly.create_cell("PCM_Ring").cell_index()
#  cell_dev=layout.cell("Ring_Jaspreet").cell_index()

  # Create a new cell
  newcellname="bias_array"
  delete_cell = layout.cell(newcellname)
  if delete_cell:
    layout.delete_cell(delete_cell.cell_index())
  top_cell = layout.create_cell(newcellname)
  
  
  cell_dev_cell=layout.cell("gc_pair")
  cell_dev=cell_dev_cell.cell_index()

  for i in range(len(bias_list)):
  
    #create new cell for each bias
    newcellname="bias"+str(int(round(bias_list[i])))
    delete_cell = layout.cell(newcellname)
    if delete_cell:
      layout.delete_cell(delete_cell.cell_index())
    new_cell = layout.create_cell(newcellname)
    
    #create new subcell for each bias
    newcellname="bias"+str(int(round(bias_list[i])))+"subcell"
    delete_cell = layout.cell(newcellname)
    if delete_cell:
      layout.delete_cell(delete_cell.cell_index())
    new_subcell = layout.create_cell(newcellname)
    
    #copy cell contents to new cell
    t = Trans(Trans.R0, 0, 0)
    new_cell.insert(CellInstArray(cell_dev, t))
  
    # resize cell components onto different layer
    shapes_high=new_subcell.shapes(layer_high)
    pya.ShapeProcessor().size(layout,new_cell,layer_in,shapes_high,bias_list[i],pya.EdgeProcessor.ModeOr,True,True,True)
    new_cell.insert(pya.CellInstArray(new_subcell.cell_index(), pya.Trans(0, 0)))
    
    # add label for each density
    t = pya.Trans(Trans.R0,xlabel_orig/dbu, ylabel_orig/dbu)
    text = pya.Text ("opt_in_TE_1550_device_bias_"+str(round(bias_list[i]))+"nm", t)
    shape = new_cell.shapes(TextLayerN).insert(text)
    shape.text_size = 500*dbu
    
    #insert cell into top_cell
    t = Trans(Trans.R0, x_offset/dbu, (y_offset+i*yspacing)/dbu)
    top_cell.insert(CellInstArray(new_cell.cell_index(), t))



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
