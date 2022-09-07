
# Enter your Python code here

from pya import *
  
# Import functions from SiEPIC-Tools, and get technology details
from SiEPIC.utils import select_paths, get_layout_variables
TECHNOLOGY, lv, ly, cell = get_layout_variables()
dbu = ly.dbu
from SiEPIC.extend import to_itype
from SiEPIC.scripts import path_to_waveguide
import glob,os
import random

# clean all cells within the present cell
ly.prune_subcells(cell.cell_index(), 10)


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
  
  GC_offset=15
  
  xspacing=80
  gap=0.1
  base_rad=30
  base_width=0.5
  ring_posx=GC_offset-base_rad-gap-base_width
  ring_posy=-60
  
  
  bias_list=[-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,15,18,20,30,40]
  random.shuffle(bias_list)
    
  #create new cell for standard loopback
  for i in range(len(bias_list)):
    newcellname="rings_bias"+str(bias_list[i])
    delete_cell = layout.cell(newcellname)
    if delete_cell:
      layout.delete_cell(delete_cell.cell_index())
    cutbackcell = layout.create_cell(newcellname)
    
    x=i*xspacing
  
    #place GCs
    cell_GC = ly.create_cell("ebeam_gc_te1550", "EBeam").cell_index()
    t = Trans(Trans.R0, x/dbu, 0/dbu)
    cutbackcell.insert(CellInstArray(cell_GC, t))
    t = Trans(Trans.R0, x/dbu, (0-127)/dbu)
    cutbackcell.insert(CellInstArray(cell_GC, t))
    
    #route waveguides
    dpath = DPath([DPoint(x,0), DPoint(x+GC_offset,0), DPoint(x+GC_offset,0-127),DPoint(x,0-127)], 0.5)
    cutbackcell.shapes(layer_in).insert(dpath.to_itype(dbu))
      
    #text labels
    t = pya.Trans(Trans.R0,(x)/dbu, (0)/dbu)
    text = pya.Text ("opt_in_TE_1550_device_Ringbiassweep&bias"+str(bias_list[i]), t)
    shape = cutbackcell.shapes(TextLayerN).insert(text)
        
    path_to_waveguide(cell = cutbackcell, verbose=True, params = 
          {'width': 0.5, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2,
          'wgs': [{'width': 0.5, 'layer': 'Si', 'offset': 0.0}]})  
          
    #place ring
    rad1=(base_rad+bias_list[i]/1000+base_width/2)
    rad2=(base_rad-bias_list[i]/1000-base_width/2)
    ring_params={"layer":pya.LayerInfo(1, 0),"actual_radius1":rad1,"actual_radius2":rad2,"npoints": 500}
    cell_ring = ly.create_cell("DONUT","Basic",ring_params)
    t = Trans(Trans.R0, (x+ring_posx-bias_list[i]/1000)/dbu, ring_posy/dbu)
    cutbackcell.insert(pya.CellInstArray(cell_ring.cell_index(), t))
    
    #cell_ring = ly.create_cell("DONUT",{"layer":pya.LayerInfo(1, 0)}).cell_index()
  
    
    topcell.insert(pya.CellInstArray(cutbackcell.cell_index(), pya.Trans(0, 0)))


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
