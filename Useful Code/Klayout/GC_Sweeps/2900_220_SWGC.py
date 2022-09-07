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
  sepx=100
  sepy=180
  
  num_rows=21
  num_cols=21
  
  pmper=0.06
  max_per=1.69+pmper
  min_per=1.69-pmper
  dper=(max_per-min_per)/(num_rows-1)
  
  pmerr=0.03
  max_err=0+pmerr
  min_err=0-pmerr
  derr=(max_err-min_err)/(num_cols-1)
  
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
  cell = cell.layout().create_cell("2900_SWG_GC")
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
  top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))
  i=0
  for row in range(num_rows):
    for col in range(num_cols):

      print("EBeam.Example_mixed_waveguide_types")
    
      perrow=min_per+dper*row #vary period by row
      errcol=min_err+derr*col #vary width error by column
      
      # Import cells from the SiEPIC Library, and instantiate them
      
      # make grating coupler
      cell_taper = ly.create_cell("SWG Fibre Grating Coupler", "EBeam-dev", 
        { "wavelength":2.9 ,"n_e":3.1,"angle_e":20,
        "grating_length":32,"taper_length":32,"dc":0.541422,"period":perrow,
        "ff":0.272739,"w_err":errcol}
        ).cell_index()
        
        
      # place grating couplers
      t = Trans(Trans.R0, col*sepx/dbu, row*sepy/dbu)
      cell.insert(CellInstArray(cell_taper, t))
      t = Trans(Trans.R0, col*sepx/dbu, row*sepy/dbu+127/dbu)
      cell.insert(CellInstArray(cell_taper, t))
        
      # Create paths for waveguides type 1, then convert path to waveguide
      dpath = DPath([DPoint(col*sepx+0,row*sepy+0), DPoint(col*sepx+20,row*sepy+0), DPoint(col*sepx+20,row*sepy+127),DPoint(col*sepx+0, row*sepy+127)], 1)
      cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))

        
    # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
      t = pya.Trans(Trans.R0,col*sepx/dbu, row*sepy/dbu)
      text = pya.Text ("opt_in_TE_2900_device_UGC_p"+str(perrow)+"_err"+str(errcol)+"_"+str(i), t)
      shape = cell.shapes(TextLayerN).insert(text)
      shape.text_size = 100
      i=i+1
      
  path_to_waveguide(cell = cell, verbose=True, params = 
    {'width': 1, 'adiabatic': True, 'radius': 20.0, 'bezier': 0.2, 
    'wgs': [{'width': 1, 'layer': 'Si', 'offset': 0.0}]})
  
    
  # finish up, unselect, zoom, show all hierarchy 
  lv.clear_object_selection()
  lv.zoom_fit()
  lv.max_hier()

  print (" done layout.")
  
Example_mixed_waveguide_types()
