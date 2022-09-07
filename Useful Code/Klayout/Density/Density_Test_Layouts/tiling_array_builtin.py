
# Enter your Python code here

import pya



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


  p = pya.AbsoluteProgress("Layout invert resist tone")
  p.format_unit = 7

  # Create new layers for the inverted layout: one high resolution, and one low resolution
  layer_high = layout.layer(pya.LayerInfo(100, 0))
  layer_in=layout.layer(pya.LayerInfo(1,0))
  layer_temp = layout.layer(pya.LayerInfo(300, 0))

  
  layer_tile = layout.layer(pya.LayerInfo(400, 0))
  
  # Create a new cell
  newcellname="tiling"
  delete_cell = layout.cell(newcellname)
  if delete_cell:
    layout.delete_cell(delete_cell.cell_index())
  cell = layout.create_cell(newcellname)
  
  
  # set up vertical array of densities
  yspacing=350-127
  densitylist=[0.2,0.4,0.6,0.8]
  
  startx=0
  endx=100
  y_offset=110
  x_offset=50
  
  mindistance=1000 #distance between pattern and nearest tiles (nm > 200)
    
    
  #create array of given device
  #cell_dev= ly.create_cell("PCM_Ring").cell_index()
  cell_dev=layout.cell("Ring_Jaspreet").cell_index()
  #topcell.insert(pya.CellInstArray(

  
  for i in range(len(densitylist)):
    # make device 
    t = Trans(Trans.R0, x_offset/dbu, (y_offset+i*yspacing)/dbu)
    topcell.insert(CellInstArray(cell_dev, t))
    
    

  
  r = ...        # region to fill
  c = layout.cell("ring_array2").cell_index()       # cell in which to produce the fill cells
  fc_index = layout.cell("fill_base").cell_index() # fill cell index
  fc_box = ...   # fill cell footprint
  
  c.fill_region(r, fc_index, fc_box, nil, r, fill_margin, nil)

  	(const Region region,
unsigned int fill_cell_index,
const Box fc_box,
const Point ptr origin)


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
