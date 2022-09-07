# Import KLayout-Python API
from pya import *

# Example layout function
def Example_mixed_waveguide_types():

  # Create a layout using different waveguide types.
  # uses:
  #  - the SiEPIC EBeam Library
  # creates the layout in the presently selected cell
  # deletes everything first
  
  #separation between adjacent rings
  sepy=30
  NUMRINGS=20
  
  

  # parameter definitions
  taper_length = 10
  wg_width1 = 0.5
  wg_width2 = 3.0
  
  num_rows=7
  num_cols=7
  
  # Import functions from SiEPIC-Tools, and get technology details
  from SiEPIC.utils import select_paths, get_layout_variables
  TECHNOLOGY, lv, ly, cell = get_layout_variables()
  dbu = ly.dbu
  from SiEPIC.extend import to_itype
  from SiEPIC.scripts import path_to_waveguide
  
  # clean all cells within the present cell
  ly.prune_subcells(cell.cell_index(), 10)
  
  # Layer mapping:
  LayerSiN = ly.layer(TECHNOLOGY['Waveguide'])
  TextLayerN = cell.layout().layer(TECHNOLOGY['Text'])
    
  # Create a sub-cell for our layout, place the cell in the top cell
  top_cell = cell
  cell = cell.layout().create_cell("WDM_top")
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
  top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))
  
  print("Placing GCs")
 # place grating couplers
  cell_GC=ly.create_cell("ebeam_gc_te1550", "EBeam").cell_index()
  for i in range(4):
    t = Trans(Trans.R0, 0, 0)
    cell.insert(CellInstArray(cell_GC, t))
    t = Trans(Trans.R0, 0, 127/dbu*i)
    cell.insert(CellInstArray(cell_GC, t))
    

  
  
  #place y branches
  cell_ybranch=ly.create_cell("ebeam_y_1550", "EBeam").cell_index()
  dxtaper=14.8
  dytaper=2.75
  xend=14.8/2
  yend=127*2
  branch_endsx=[]
  branch_endsy=[]
  for i in range(NUMRINGS-1):
    xstart=xend
    ystart=yend
    t=Trans(Trans.R0,(xstart)/dbu,(ystart)/dbu)
    cell.insert(CellInstArray(cell_ybranch,t))
    xend=dxtaper+xstart
    yend=dytaper+ystart
    branch_endsx.append(xend)
    branch_endsy.append(yend-2*dytaper)
  branch_endsx.append(xend)
  branch_endsy.append(yend)
    
  #place rings
  xstartr=dxtaper*(NUMRINGS)+50
  ystartr=127*2-sepy*NUMRINGS
  dyrings=sepy
  xrings=[]
  yrings=[]
  for i in range(NUMRINGS):
    xpos=xstartr
    ypos=ystartr+i*dyrings
    xrings.append(xpos)
    yrings.append(ypos)
    
    cell_ring=cell_taper = ly.create_cell("DoubleBus_Ring", "EBeam-dev", 
        {"r":10}
        ).cell_index()
    #cell_ybranch=ly.create_cell("ebeam_y_1550", "EBeam").cell_index()
    t = Trans(Trans.R0, xpos/dbu, ypos/dbu)
    cell.insert(CellInstArray(cell_ring, t))
  
  #route waveguides from branches to rings
  xoffset=0
  normoffset=10
  for i in range(NUMRINGS):
    if i==NUMRINGS-1:
      xoffset=dxtaper
    else:
      xoffset=0
    dpath = DPath([DPoint(branch_endsx[i],branch_endsy[i]), DPoint(branch_endsx[i]+xoffset+normoffset,branch_endsy[i]),
     DPoint(branch_endsx[i]+xoffset+normoffset,yrings[i]),DPoint(xrings[i], yrings[i])], 0.5)
    cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
    path_to_waveguide(cell = cell, verbose=True, params = 
      {'width': wg_width1, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
      'wgs': [{'width': wg_width1, 'layer': 'Si', 'offset': 0.0}]})
  
  #place combining y-branches
  diam_ring=20
  cell_ybranch2=ly.create_cell("ebeam_y_1550", "EBeam").cell_index()
  dxtaper2=-14.8
  dytaper=2.75
  xend=xrings[1]*2+diam_ring
  yend=branch_endsy[1]
  branch_endsx2=[]
  branch_endsy2=[]
  for i in range(NUMRINGS-1):
    xstart=xend
    ystart=yend
    t=Trans(Trans.R180,(xstart)/dbu,(ystart)/dbu)
    cell.insert(CellInstArray(cell_ybranch,t))
    xend=dxtaper2+xstart
    yend=dytaper+ystart
    branch_endsx2.append(xend)
    branch_endsy2.append(yend-2*dytaper)
  branch_endsx2.append(xend)
  branch_endsy2.append(yend)
  
  #route to combining y-branches
  xoffset=0
  normoffset=-10
  for i in range(NUMRINGS):
    if i==NUMRINGS-1:
      xoffset=-dxtaper
    else:
      xoffset=0
    dpath = DPath([DPoint(branch_endsx2[i],branch_endsy2[i]), DPoint(branch_endsx2[i]+xoffset+normoffset,branch_endsy2[i]),
     DPoint(branch_endsx2[i]+xoffset+normoffset,yrings[i]),DPoint(xrings[i]+diam_ring, yrings[i])], 0.5)
    cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
    path_to_waveguide(cell = cell, verbose=True, params = 
      {'width': wg_width1, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
      'wgs': [{'width': wg_width1, 'layer': 'Si', 'offset': 0.0}]})

  #route end of combiner to GC
  overextend=20
  dpath = DPath([DPoint(branch_endsx2[0]+dxtaper,branch_endsy2[0]+dytaper), 
   DPoint(branch_endsx2[0]+dxtaper+overextend,branch_endsy2[0]+dytaper),
   DPoint(branch_endsx2[0]+dxtaper+overextend,127*3),DPoint(0,127*3)], 0.5)
  cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
  path_to_waveguide(cell = cell, verbose=True, params = 
    {'width': wg_width1, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
    'wgs': [{'width': wg_width1, 'layer': 'Si', 'offset': 0.0}]})
  
  
  
  # Create paths for waveguides type 1, then convert path to waveguide
  dpath = DPath([DPoint(0,0), DPoint(10,0), DPoint(10,127),DPoint(0, 127)], 0.5)
  cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
  path_to_waveguide(cell = cell, verbose=True, params = 
    {'width': wg_width1, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
    'wgs': [{'width': wg_width1, 'layer': 'Si', 'offset': 0.0}]})
    
# Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
  t = pya.Trans(Trans.R0,0, 0)
  text = pya.Text ("opt_in_TE_1550_device_WDM_input1", t)
  shape = cell.shapes(TextLayerN).insert(text)
  shape.text_size = 10*dbu
  

  # finish up, unselect, zoom, show all hierarchy 
  lv.clear_object_selection()
  lv.zoom_fit()
  lv.max_hier()

  print (" done layout.")
  
Example_mixed_waveguide_types()
