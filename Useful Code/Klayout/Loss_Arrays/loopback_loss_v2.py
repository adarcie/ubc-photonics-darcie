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
  sepx=160
  sepy=180
  
  
  

  # parameter definitions
  taper_length = 0
  wg_width1 = 0.5
  wg_width2 = 3.0
  
  bend_radius=10
  
  num_rows=1
  num_cols=1
  
  maxx=8000
  maxy=4800
  
  maxdlength=7000
  mindlength=10
  ddlength=100
  dlengthlist=[]
  dlength=maxdlength
  while dlength>=mindlength:
    dlengthlist.append(dlength)
    dlength=dlength-ddlength
  
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
  cell = cell.layout().create_cell("example_cell")
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
  top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))
  
  xcoord=0
  ycoord=0
  while ycoord+127<maxy:
    xcoord=0
    for dlength in dlengthlist:
      if dlength+xcoord+sepx<maxx+40:
        dlengthlist.remove(dlength)
  
        print("cutback_losses")
      
        
        
        # Import cells from the SiEPIC Library, and instantiate them
        xsize=78
        ysize=50
        a=0.243
        # make grating coupler
        cell_taper = ly.cell("1550_220_gc_new").cell_index()
        
        # place grating couplers
        t = Trans(Trans.R0, (xcoord)/dbu, ycoord/dbu)
        cell.insert(CellInstArray(cell_taper, t))
        t = Trans(Trans.R0, (xcoord)/dbu, ycoord/dbu+127/dbu)
        cell.insert(CellInstArray(cell_taper, t))
      
        wg_width1 = 0.5#wg_width
        wg_width2 = a*(ysize-4)

        
        
      
        
        xlength=dlength
        # Create paths for waveguides type 1, then convert path to waveguide
        dpath = DPath([DPoint(xcoord+0,ycoord+0), DPoint(xcoord+xlength,ycoord+0), DPoint(xcoord+xlength,ycoord+127),DPoint(xcoord+0, ycoord+127)], 0.5)
        cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        path_to_waveguide(cell = cell, verbose=True, params = 
          {'width': wg_width1, 'adiabatic': True, 'radius': bend_radius, 'bezier': 0.2, 
          'wgs': [{'width': wg_width1, 'layer': 'Si', 'offset': 0.0}]})
          
        
        
          
          
      # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
        pathlength=xlength*2+127-4*bend_radius+3.14159265*bend_radius+2.4 #assumes circular, not bezier but should be close within reason
      
        t = pya.Trans(Trans.R0,xcoord/dbu, (ycoord+127)/dbu)
        text = pya.Text ("opt_in_TE_1550_device_loss_"+str(round(pathlength)), t)
        shape = cell.shapes(TextLayerN).insert(text)
        shape.text_size = 100*dbu
        
        xcoord=xcoord+dlength+sepx

    ycoord=ycoord+sepy
    
  
  calcoordsx=[-300,-300,maxx+150,maxx+150]
  calcoordsy=[-200,maxy+10,maxy+10,-200]
  
  for i in range(len(calcoordsx)):
    xcoord=calcoordsx[i]
    ycoord=calcoordsy[i]
    
    # Import cells from the SiEPIC Library, and instantiate them

    # make grating coupler
    cell_taper = ly.cell("1550_220_gc_new").cell_index()
      
    # place grating couplers
    t = Trans(Trans.R0, (xcoord)/dbu, ycoord/dbu)
    cell.insert(CellInstArray(cell_taper, t))
    t = Trans(Trans.R0, (xcoord)/dbu, ycoord/dbu+127/dbu)
    cell.insert(CellInstArray(cell_taper, t))
  
    wg_width1 = 0.5#wg_width
    wg_width2 = a*(ysize-4)
    
  

    xlength=dlength
    # Create paths for waveguides type 1, then convert path to waveguide
    dpath = DPath([DPoint(xcoord+0,ycoord+0), DPoint(xcoord+bend_radius,ycoord+0), DPoint(xcoord+bend_radius,ycoord+127),DPoint(xcoord+0, ycoord+127)], 0.5)
    cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
    
    path_to_waveguide(cell = cell, verbose=True, params = 
      {'width': wg_width1, 'adiabatic': True, 'radius': bend_radius, 'bezier': 0.2, 
      'wgs': [{'width': wg_width1, 'layer': 'Si', 'offset': 0.0}]})
      
  
    t = pya.Trans(Trans.R0,xcoord/dbu, (ycoord+127)/dbu)
    text = pya.Text ("opt_in_TE_1550_device_strloss_cal_"+str(i), t)
    shape = cell.shapes(TextLayerN).insert(text)
    shape.text_size = 100*dbu
          
      
  # finish up, unselect, zoom, show all hierarchy 
  lv.clear_object_selection()
  lv.zoom_fit()
  lv.max_hier()

  print (" done layout.")
      

  
Example_mixed_waveguide_types()
