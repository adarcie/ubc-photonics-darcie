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
  
  
  # parameter definitions
  end_length=50
  n_lengths=20
  DC_lengths=list(range(n_lengths))
  DC_lengths = [x *50/20 for x in DC_lengths]
  print(DC_lengths)
  sepx=100#um
  xoffset=15#um - distance of DC from GC
  xstart=0
  ystart=0
  
  dc_wgsep=4.7#distance between two waveguides at end of DC (measured)
  dc_taperlength=7#length of coupler minus coupling region
  wg_overshoot=20#distance the far wg will be from the edge of the coupler
  
  # specify GC cell
  cell_GC = ly.create_cell("ebeam_gc_te1550", "EBeam").cell_index()
    
  # Create a sub-cell for our layout, place the cell in the top cell
  top_cell = cell
  cell = cell.layout().create_cell("DC_Sweep_Cell")
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
  top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))
  
  for col in range(len(DC_lengths)):
  
    dc_length=DC_lengths[col]
    full_comp_length=dc_length+dc_taperlength
    print("Starting DC length: ",str(dc_length))
    
    # Import cells from the SiEPIC Library, and instantiate them

    #coords of input GC
    x=xstart+col*sepx
    y=ystart
    

      
      
    # place grating couplers
    t = Trans(Trans.R0, x/dbu, y/dbu)
    cell.insert(CellInstArray(cell_GC, t))
    t = Trans(Trans.R0, x/dbu, (y+127)/dbu)
    cell.insert(CellInstArray(cell_GC, t))
    t = Trans(Trans.R0, x/dbu, (y-127)/dbu)
    cell.insert(CellInstArray(cell_GC, t)) 
    
    
    # origin of DC
    dc_origx=(x+xoffset)
    dc_origy=(y-127/2)
    
    # place DC
    dc_params={"silayer":pya.LayerInfo(1, 0),"Lc":dc_length,"pinrec":pya.LayerInfo(1, 10),"devrec":pya.LayerInfo(68, 0),"textl":pya.LayerInfo(10, 0)}
    cell_DC = ly.create_cell("ebeam_dc_te1550","EBeam",dc_params)
    t = Trans(Trans.R90, dc_origx/dbu, (y-127/2)/dbu)
    cell.insert(pya.CellInstArray(cell_DC.cell_index(), t))
    
    #determine DC WG placements
    inx=dc_origx-dc_wgsep/2
    iny=dc_origy+full_comp_length/2
    
    outblx=dc_origx-dc_wgsep/2
    outbly=dc_origy-full_comp_length/2
    
    outbrx=dc_origx+dc_wgsep/2
    outbry=dc_origy-full_comp_length/2
    
    outtrx=dc_origx+dc_wgsep/2
    outtry=dc_origy+full_comp_length/2
    
    #route input waveguide
    dpath = DPath([DPoint(x,y), DPoint(inx,y), DPoint(inx,iny)], 0.5)
    cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
    
    #route output bl waveguide to bottom coupler
    dpath = DPath([DPoint(x,y-127), DPoint(outblx,y-127), DPoint(outblx,outbly)], 0.5)
    cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
    
    #route output br waveguide to top coupler
    dpath = DPath([DPoint(x,y+127), DPoint(outbrx+wg_overshoot,y+127), 
      DPoint(outbrx+wg_overshoot,outbry-wg_overshoot), DPoint(outbrx,outbry-wg_overshoot),DPoint(outbrx,outbry)], 0.5)
    cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
    
    #add terminator to remaining port
    cell_term = ly.create_cell("ebeam_terminator_te1550", "EBeam").cell_index()
    t = Trans(Trans.R270, outtrx/dbu, (outtry+2.50)/dbu)
    cell.insert(CellInstArray(cell_term, t)) 
    
    # Create paths for waveguides type 1, then convert path to waveguide
    #dpath = DPath([DPoint(col*sepx+0,row*sepy+0), DPoint(col*sepx+10,row*sepy+0), DPoint(col*sepx+10,row*sepy+127),DPoint(col*sepx+0, row*sepy+127)], 0.5)
    #cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
    path_to_waveguide(cell = cell, verbose=True, params = 
      {'width': 0.5, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2,
      'wgs': [{'width': 0.5, 'layer': 'Si', 'offset': 0.0}]})
      
  # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
    t = pya.Trans(Trans.R0,x/dbu, y/dbu)
    text = pya.Text ("opt_in_TE_1550_PCM_PCM&DC&"+str(dc_length), t)
    shape = cell.shapes(TextLayerN).insert(text)
    shape.text_size = 10*dbu
    
  
    # finish up, unselect, zoom, show all hierarchy 
    lv.clear_object_selection()
    lv.zoom_fit()
    lv.max_hier()
    
    print (" done")
  
Example_mixed_waveguide_types()
