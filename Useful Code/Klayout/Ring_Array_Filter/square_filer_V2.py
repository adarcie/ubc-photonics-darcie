
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
  
  # parameter definitions
  num_rows=3
  num_cols=3
  
  startx=50
  starty=0
  
  wgwidth=0.5
  

  
  gap=0.1
  #parameters for current ring      
  radius=10.0
  L_straight=8.0
  
  L_cav=round((2*L_straight+2*3.1415927*radius)*1000)/1000
  L_B=round(L_cav/2)
  sepx=L_B  

  print("EBeam.Example_mixed_waveguide_types")
  
  
  #arrange rings
  for col in range(num_cols):
    y=starty
    x=(startx+sepx*col)
    for row in range(num_rows):

      wg_width=0.5
      start_angle=0
      stop_angle=360
      
      y=(gap*(row+1)+wg_width*(row+1)+radius*(1+2*row))
      endy=y
      
      
      # Import cells from the SiEPIC Library, and instantiate them
      
      # left arc
      cell_ring = ly.create_cell("Waveguide_Arc", "EBeam-dev",
      {"radius":radius,"wg_width":wg_width,"start_angle":90,"stop_angle":270}
      ).cell_index()
        
      t = Trans(Trans.R0, x/dbu, y/dbu)
      cell.insert(CellInstArray(cell_ring, t))
      
      # right arc

      #t = Trans(Trans.R180, (x+L_straight)/dbu, y/dbu)
      #cell.insert(CellInstArray(cell_ring, t))
      
      cell_ring = ly.create_cell("Waveguide_Arc", "EBeam-dev",
      {"radius":radius,"wg_width":wg_width,"start_angle":90,"stop_angle":270}
      ).cell_index()
        
      t = Trans(Trans.R180, (x+L_straight)/dbu, y/dbu)
      cell.insert(CellInstArray(cell_ring, t))
      
      
      
      #connect halves with waveguides
      
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
      
      
      #dpath = DPath([DPoint(x,y-radius), DPoint(x+L_straight,y-radius)], 0.5)
      #cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
      #dpath = DPath([DPoint(x,y+radius), DPoint(x+L_straight,y+radius)], 0.5)
      #cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        
      # finish up, unselect, zoom, show all hierarchy 
      lv.clear_object_selection()
      lv.zoom_fit()
      lv.max_hier()
    
      print (" done layout.")
      
  #place grating couplers
  coupleroffset=100
  cell_gc = ly.create_cell("ebeam_gc_te1550", "EBeam").cell_index()
  for i in range(4):
    t = Trans(Trans.R0, (startx-coupleroffset)/dbu, (starty+127*(i-1))/dbu)
    cell.insert(CellInstArray(cell_gc, t))
    
  #route waveguides
  xbuffer=0
  ybuffer=0
  dpath = DPath([DPoint(startx-coupleroffset,starty), DPoint(startx+num_cols*sepx+xbuffer,starty), 
  DPoint(startx+num_cols*sepx+xbuffer,starty-127),DPoint(startx-coupleroffset,starty-127)], 0.5)
  cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
    
  
  xcorner=50  
  dpath = DPath([DPoint(startx-coupleroffset,starty-wgwidth/2+127), DPoint(startx-coupleroffset+xcorner,starty-wgwidth/2+127), 
  DPoint(startx-coupleroffset+xcorner,endy+radius+wg_width+gap),DPoint(startx+num_cols*sepx+xbuffer,endy+radius+wg_width+gap),
  DPoint(startx+num_cols*sepx+xbuffer,starty-wgwidth/2+127*2),DPoint(startx-coupleroffset,starty-wgwidth/2+127*2)], 0.5)
  cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
  #path_to_waveguide(cell = cell, verbose=True, params = 
   # {'width': 0.5, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
    #'wgs': [{'width': 0.5, 'layer': 'Si', 'offset': 0.0}]})
    
  #dpath = DPath([DPoint(startx-coupleroffset,starty-wgwidth/2+127), DPoint(startx+num_cols*sepx+xbuffer,starty-wgwidth/2), 
  #DPoint(startx+num_cols*sepx+xbuffer,starty-127),DPoint(startx-coupleroffset,starty-127)], 0.5)
  #cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
  path_to_waveguide(cell = cell, verbose=True, params = 
    {'width': 0.5, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
    'wgs': [{'width': 0.5, 'layer': 'Si', 'offset': 0.0}]})
    
  # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
  t = pya.Trans(Trans.R0, (startx-coupleroffset)/dbu, (starty+127*1)/dbu)
  text = pya.Text ("opt_in_TE_1550_device_ringfilter_1", t)
  shape = cell.shapes(TextLayerN).insert(text)
  shape.text_size = 10*dbu
    
    



Example_mixed_waveguide_types()

