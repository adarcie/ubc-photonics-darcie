import pya
import numpy as np


from SiEPIC.utils import select_paths, get_layout_variables
TECHNOLOGY, lv, ly, cell = get_layout_variables()
dbu = ly.dbu
from SiEPIC.extend import to_itype
from SiEPIC.scripts import path_to_waveguide

taper_length = 20
wg_width1 = 0.5
wg_width2 = 3.0

ly.prune_subcells(cell.cell_index(), 10)
  
# Layer mapping:
LayerSiN = ly.layer(TECHNOLOGY['Waveguide'])
TextLayerN = cell.layout().layer(TECHNOLOGY['Text'])
  
# Create a sub-cell for our layout, place the cell in the top cell
top_cell = cell
cell = cell.layout().create_cell("example_cell")
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))


  
#make a circular waveguide
to_dpath=[]
to_dpath_bottom=[]
for x in range(-30,31):
  y=np.sqrt(30**2-x**2)
  to_dpath.append(DPoint(x,y))
  to_dpath_bottom.append(DPoint(-x,-y))
to_dpath.extend(to_dpath_bottom)
  
print(to_dpath)
  
dpath=DPath(to_dpath,0.5)
cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
path_to_waveguide(cell = cell, verbose=True, params = 
  {'width': wg_width1, 'adiabatic': True, 'radius': 0, 'bezier': 0.2, 
  'wgs': [{'width': wg_width2, 'layer': 'Si', 'offset': 0.0}]})
  
#add grating coupler
pcell = ly.create_cell("ebeam_gc_te1550", "EBeam")
cell.insert(CellInstArray(pcell.cell_index(),Trans(Trans.R0,30000,0)))


  

# finish up, unselect, zoom, show all hierarchy 
lv.clear_object_selection()
lv.zoom_fit()
lv.max_hier()


#lv.write("pythontests.gds")