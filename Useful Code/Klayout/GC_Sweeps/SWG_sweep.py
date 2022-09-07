# Import KLayout-Python API
from pya import *

# Example layout function
def Example_mixed_waveguide_types():

  # Create a layout using different waveguide types.
  # uses:
  #  - the SiEPIC EBeam Library
  # creates the layout in the presently selected cell
  # deletes everything first
  
  #separation between adjacent couplers in x and y
  sepx=70
  sepy=180
  
  
  

  # parameter definitions
  taper_length = 10
  wg_width1 = 0.5
  wg_width2 = 3.0
  
  num_rows=21
  num_cols=21
  
  maxffl=0.3
  minffl=0.1
  mindc=0.38
  maxdc=0.48
  
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
  cell = cell.layout().create_cell("SWG_sweep_cell")
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
  top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))
  
  for row in range(num_rows):
    for col in range(num_cols):

      print("EBeam.Example_mixed_waveguide_types")
      
      
      curffl = minffl+(maxffl-minffl)*row/(num_rows-1)
      curdc = mindc+(maxdc-mindc)*col/(num_cols-1)
      
      
      # Import cells from the SiEPIC Library, and instantiate them
      
      # make grating coupler
      cell_taper = ly.create_cell("Focusing Sub-wavelength grating coupler (fswgc)", "EBeam-dev", 
        {"theta_c":10, "wavelength":1.55,"t":0.5,"Si_thickness":0.2,"etch_depth":0.2,"angle_e":35,"taper_length":19,"grating_length":15,"period":0.468,"dc":curdc,"ff":curffl}
        ).cell_index()
        
        
      # place grating couplers
      t = Trans(Trans.R0, col*sepx/dbu, row*sepy/dbu)
      cell.insert(CellInstArray(cell_taper, t))
      t = Trans(Trans.R0, col*sepx/dbu, row*sepy/dbu+127/dbu)
      cell.insert(CellInstArray(cell_taper, t))
        
      # Create paths for waveguides type 1, then convert path to waveguide
      dpath = DPath([DPoint(col*sepx+0,row*sepy+0), DPoint(col*sepx+10,row*sepy+0), DPoint(col*sepx+10,row*sepy+127),DPoint(col*sepx+0, row*sepy+127)], 0.5)
      cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
      path_to_waveguide(cell = cell, verbose=True, params = 
        {'width': wg_width1, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
        'wgs': [{'width': wg_width1, 'layer': 'Si', 'offset': 0.0}]})
        
    # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
      t = pya.Trans(Trans.R0,col*sepx/dbu, row*sepy/dbu)
      text = pya.Text ("opt_in_TE_1550_device_SWG_"+str(row)+"_"+str(col), t)
      shape = cell.shapes(TextLayerN).insert(text)
      shape.text_size = 10*dbu
      
    
      # finish up, unselect, zoom, show all hierarchy 
      lv.clear_object_selection()
      lv.zoom_fit()
      lv.max_hier()
    
      print (" done layout.")
  
Example_mixed_waveguide_types()
