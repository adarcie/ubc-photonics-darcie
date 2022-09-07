
# Import KLayout-Python API
from pya import *

# Example layout function
def Example_mixed_waveguide_types():

  # Create a layout using different waveguide types.
  # uses:
  #  - the SiEPIC EBeam Library
  # creates the layout in the presently selected cell
  # deletes everything first
  

  
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
  cell = cell.layout().create_cell("rings")
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
  top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))
  
  #separation between adjacent couplers in x and y
  sepx=25
  
  #specify gap spacing in y
  gapylist=[200,460,200]
  
  # parameter definitions
  num_rows=2
  num_cols=10
  
  startx=50
  starty=0
  
  wgwidth=0.5
  
  gap=0.1
  #parameters for current ring      
  radius=10.0
  L_straight=0
  
  L_cav=((2*L_straight+2*3.1415926535*radius)*1000)/1000
  L_B=(L_cav/2)
  sepx=L_B*2
  
  tail_offset=radius/2

  print("EBeam.Example_mixed_waveguide_types")
  
  
  #arrange rings
  for col in range(num_cols):
    y=starty
    x=(startx+sepx*col)
    for row in range(num_rows):

      wg_width=0.5
      
      gap=gapylist[row]/1000
      
      gap_y_pos=sum(gapylist[:row+1])/1000
      
      #y=(gap*(row+1)+wg_width*(row+1)+radius*(1+2*row))
      y=(gap_y_pos+wg_width*(row+1)+radius*(1+2*row))
      endy=y
      
      
      # Import cells from the SiEPIC Library, and instantiate them
      

      
      
      
      #place connecting waveguides
      
      cell_ring = ly.create_cell("Waveguide_Straight", "EBeam",
      {"wg_length":(L_straight)/dbu,"wg_width":wg_width/dbu}
      ).cell_index()
      t = Trans(Trans.R0, (x+L_straight/2)/dbu, (y-radius)/dbu)
      cell.insert(CellInstArray(cell_ring, t))
      cell_ring = ly.create_cell("Waveguide_Straight", "EBeam",
      {"wg_length":(L_straight)/dbu,"wg_width":wg_width/dbu}
      ).cell_index()
      t = Trans(Trans.R0, (x+L_straight/2)/dbu, (y+radius)/dbu)
      cell.insert(CellInstArray(cell_ring, t))
      
      
      # left arc
      
      dpath = DPath([DPoint(x,y+radius), DPoint(x-radius,y+radius), 
      DPoint(x-radius,y-radius),DPoint(x,y-radius)], 0.5)
      cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
      
      # right arc
      
      dpath = DPath([DPoint(x+L_straight,y+radius), DPoint(x+L_straight+radius,y+radius), 
      DPoint(x+L_straight+radius,y-radius),DPoint(x+L_straight,y-radius)], 0.5)
      cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
      
  # place broken waveguides and terminators
  side="top"    
  for col in range(num_cols-1):
    width_join=sepx+tail_offset*2
  
    x=(startx+sepx*(col)*(1))+0.5*width_join-(width_join-sepx)/2
    
    cell_wg = ly.create_cell("Waveguide_Straight", "EBeam",
    {"wg_length":(width_join)/dbu,"wg_width":wg_width/dbu}
    ).cell_index()
      
    if side=="bottom":
      y=starty
      side="top"
    else:
      y=endy+radius+wg_width+gapylist[-1]/1000
      side="bottom"
    t = Trans(Trans.R0, (x)/dbu, (y)/dbu)
    cell.insert(CellInstArray(cell_wg, t))
    
    #place left terminator for each pair
    cell_term = ly.create_cell("ebeam_terminator_te1550", "EBeam").cell_index()
    t2 = Trans(Trans.R0, (x-width_join/2)/dbu,(y)/dbu)
    cell.insert(CellInstArray(cell_term, t2))
    
    #place right terminator (except on last loop)
    if col<(num_cols-2):
      cell_term = ly.create_cell("ebeam_terminator_te1550", "EBeam").cell_index()
      t2 = Trans(Trans.R180, (x+width_join/2)/dbu,(y)/dbu)
      cell.insert(CellInstArray(cell_term, t2))
  
      
  path_to_waveguide(cell = cell, verbose=True, params = 
   {'width': 0.5, 'adiabatic': False, 'radius': radius, 'bezier': 0.2, 
   'wgs': [{'width': 0.5, 'layer': 'Si', 'offset': 0.0}]})
   

  #place grating couplers
  coupleroffset=30
  cell_gc = ly.create_cell("ebeam_gc_te1550", "EBeam").cell_index()
  for i in range(3):
    t = Trans(Trans.R0, (startx-coupleroffset)/dbu, (starty+127*(i-1))/dbu)
    cell.insert(CellInstArray(cell_gc, t))
    
  #route waveguides between grating couplers
  xbuffer=-15
  ybuffer=0
  
  #dpath = DPath([DPoint(startx-coupleroffset,starty), DPoint(startx+num_cols*sepx+xbuffer,starty), 
  #DPoint(startx+num_cols*sepx+xbuffer,starty-127),DPoint(startx-coupleroffset,starty-127)], 0.5)
  #cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
  
  dpath = DPath([DPoint(startx-coupleroffset,starty), DPoint(startx+tail_offset,starty)], 0.5)
  cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
  
  cell_term = ly.create_cell("ebeam_terminator_te1550", "EBeam").cell_index()
  t2 = Trans(Trans.R180, (startx+tail_offset)/dbu,(starty)/dbu)
  cell.insert(CellInstArray(cell_term, t2))
  
  
  dpath = DPath([DPoint(startx+(num_cols-1)*sepx-tail_offset,starty), DPoint(startx+num_cols*sepx+xbuffer,starty), 
  DPoint(startx+num_cols*sepx+xbuffer,starty-127),DPoint(startx-coupleroffset,starty-127)], 0.5)
  cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
  
  cell_term = ly.create_cell("ebeam_terminator_te1550", "EBeam").cell_index()
  t2 = Trans(Trans.R0, (startx+(num_cols-1)*sepx-tail_offset)/dbu,(starty)/dbu)
  cell.insert(CellInstArray(cell_term, t2))
  
  
    
  xcorner=coupleroffset/2  

  dpath = DPath([DPoint(startx-coupleroffset,starty-wgwidth/2+127),DPoint(startx+num_cols*sepx+xbuffer,starty-wgwidth/2+127),
  DPoint(startx+num_cols*sepx+xbuffer,endy+radius+wg_width+gapylist[-1]/1000),DPoint(startx+(num_cols-1)*sepx+tail_offset,endy+radius+wg_width+gapylist[-1]/1000)], 0.5)
  cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))  
  
  #place terminator for add port
  
  

  path_to_waveguide(cell = cell, verbose=True, params = 
    {'width': 0.5, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
    'wgs': [{'width': 0.5, 'layer': 'Si', 'offset': 0.0}]})
    
  # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
  t = pya.Trans(Trans.R0, (startx-coupleroffset)/dbu, (starty)/dbu)
  optlabel="opt_in_TE_1550_device_ringfilter_terminated_"+str(num_rows)+"x"+str(num_cols)+"_"+str(radius)+"nmRad"
  text = pya.Text (optlabel, t)
  shape = cell.shapes(TextLayerN).insert(text)
  shape.text_size = 10*dbu
    
    
  # finish up, unselect, zoom, show all hierarchy 
  lv.clear_object_selection()
  lv.zoom_fit()
  lv.max_hier()

  print (" done layout.")


Example_mixed_waveguide_types()

