# Import KLayout-Python API
from pya import *

from io import StringIO 
import sys

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout
        

# Example layout function
def Example_mixed_waveguide_types():

  # Create a layout using different waveguide types.
  # uses:
  #  - the SiEPIC EBeam Library
  # creates the layout in the presently selected cell
  # deletes everything first
  
  #separation between adjacent couplers in x and y
  sepx1=80
  sepy=500
  
  gc_xoffset=10
  spiral_y_offset=127/2
  
  print("start")
  
  min_bend_radius=10
  

  # parameter definitions
  taper_length = 10
  wg_width1 = 0.5
  wg_width2 = 3.0
  f
  num_rows=1
  num_cols=15
  
  path2wg=True

  
  startR=10 #um ring radius
  endR=10
  
  ring_radius=10
  
  startg=0.1
  endg=0.4
  
  WG_width_list=[0.5]#um
  sep_widths=2000#separation between adjacent width groups
  
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
  LayerPinRec = cell.layout().layer(TECHNOLOGY['PinRec'])
    
  # Create a sub-cell for our layout, place the cell in the top cell
  top_cell = cell
  
  
  for width_ind in range(len(WG_width_list)):
    WG_width=WG_width_list[width_ind]
    cell = top_cell.layout().create_cell("ring_sweep_cell_WG"+str(WG_width))
  #  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
    top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))
    
    
    
    xorigin=width_ind*sep_widths#add this offset to everything that is placed
    
    #give ratio for GC taper (slope) - used to calculate additional taper for smaller waveguides
    taper_ratio=0.1/0.4
    taper_dh=(0.5-WG_width)/2
    taper_length=taper_dh/taper_ratio
    
    for row in range(num_rows):#loop over rows (gap spacing)
      for col in range(num_cols):#loop over columns (ring radius)
  
        print("EBeam.ring_sweep")
        
        
      
        gap=startg+(endg-startg)/(num_cols-1)*col
        radius=ring_radius
          
        
        newcellname="ring_r"+str(round(radius))+"_g"+str(round(gap*1000))+"_WG"+str(round(WG_width*1000))
        delete_cell = ly.cell(newcellname)
        if delete_cell:
          ly.delete_cell(delete_cell.cell_index())
        top_ring_cell = ly.create_cell(newcellname)
        
        
        #place ring structure and get determine sizes
        cell_ring = ly.create_cell("ebeam_dc_halfring_straight", "EBeam", { "r": radius, "g": gap, "w":WG_width} )
        #determine size of spiral and set additional GC offset
        w=cell_ring.bbox().width()
        h=cell_ring.bbox().height()
        add_GC_offset=h/2*dbu#use height since cell is rotated
        
  
            
        sepx=add_GC_offset+sepx1
        
        addx=0
        realcol=col
            
        #place rings
        t = Trans(Trans.R270, (realcol*sepx+addx+xorigin)/dbu, (row*sepy+spiral_y_offset)/dbu)
        top_ring_cell.insert(CellInstArray(cell_ring.cell_index(), t))
        t = Trans(Trans.R90, (realcol*sepx+addx-(0.2-gap)*2-0.2+xorigin)/dbu+w, (row*sepy+spiral_y_offset)/dbu)
        top_ring_cell.insert(CellInstArray(cell_ring.cell_index(), t))
        
  
        
        #determine pin locations for GC routing
        pin_locs=find_PCell_pins(top_ring_cell,LayerPinRec) #only for rightmost ring half
        print(pin_locs)
        scalefac=dbu
        pin1x=float(pin_locs['pin1_x'])*scalefac
        pin1y=float(pin_locs['pin1_y'])*scalefac
        pin2x=float(pin_locs['pin2_x'])*scalefac
        pin2y=float(pin_locs['pin2_y'])*scalefac
        pin3x=float(pin_locs['pin3_x'])*scalefac
        pin3y=float(pin_locs['pin3_y'])*scalefac
        pin4x=float(pin_locs['pin4_x'])*scalefac
        pin4y=float(pin_locs['pin4_y'])*scalefac
        
        
        
        gcx=realcol*sepx-gc_xoffset-add_GC_offset+addx+xorigin
        
        gcy=row*sepy
        
        # place grating couplers
        cell_taper = ly.create_cell("ebeam_gc_te1550","EBeam").cell_index()
        t = Trans(Trans.R0, (gcx)/dbu, gcy/dbu)
        top_ring_cell.insert(CellInstArray(cell_taper, t))
        t = Trans(Trans.R0, (gcx)/dbu, gcy/dbu+127/dbu)
        top_ring_cell.insert(CellInstArray(cell_taper, t))
        #t = Trans(Trans.R0, (gcx)/dbu, gcy/dbu-127/dbu)
        #top_ring_cell.insert(CellInstArray(cell_taper, t))
        t = Trans(Trans.R0, (gcx)/dbu, gcy/dbu+254/dbu)
        top_ring_cell.insert(CellInstArray(cell_taper, t))
        
        
        #route top waveguide to pin1
        dpath = DPath([DPoint(gcx+taper_length,gcy),DPoint((2*pin4x-pin1x+taper_length/2),gcy),DPoint((2*pin4x-pin1x+taper_length/2),pin1y)], WG_width)
        top_ring_cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        #route bottom waveguide to pin3
        dpath = DPath([DPoint(gcx+taper_length,gcy+127),DPoint((2*pin4x-pin1x+taper_length/2),gcy+127),DPoint((2*pin4x-pin1x+taper_length/2),pin3y)], WG_width)
        top_ring_cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        
        #route top waveguide to pin1
        #dpath = DPath([DPoint(gcx+taper_length,gcy-127),DPoint(pin1x,gcy-127),DPoint(pin1x,pin1y)], WG_width)
        #top_ring_cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        #route bottom waveguide to pin3
        dpath = DPath([DPoint(gcx+taper_length,gcy+254),DPoint(pin3x,gcy+254),DPoint(pin3x,pin3y)], WG_width)
        top_ring_cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        
        #place terminators
        cell_term = ly.create_cell("ebeam_terminator_te1550","EBeam")
        t = Trans(Trans.R90, (pin1x)/dbu, (pin1y)/dbu)
        top_ring_cell.insert(CellInstArray(cell_term.cell_index(), t))
        #t = Trans(Trans.R270, (2*pin4x-pin1x)/dbu, (pin3y)/dbu)
        #top_ring_cell.insert(CellInstArray(cell_term.cell_index(), t))
          
          
      # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
        t = pya.Trans(Trans.R0,(gcx)/dbu, (row*sepy+127)/dbu)
        text=pya.Text ("opt_in_TE_1550_PCM_ringloss4pt&r"+str(radius)+"&g"+str(round(1e3*gap))+"&WG"+str(round(1e3*WG_width)), t)
        shape = top_ring_cell.shapes(TextLayerN).insert(text)
        shape.text_size = 10*dbu
        
        
        
        cell.insert(CellInstArray(top_ring_cell.cell_index(), Trans.R0))
              
        
      if path2wg:  
        path_to_waveguide(cell = cell, verbose=True, params = 
            {'width': wg_width1, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
            'wgs': [{'width': WG_width, 'layer': 'Si', 'offset': 0.0}]})
          
  
      
      # finish up, unselect, zoom, show all hierarchy 
      lv.clear_object_selection()
      lv.zoom_fit()
      lv.max_hier()
    
    print (" done layout.")
      
def find_PCell_pins(subcell,LayerPinRec):
  # find the location of the pins in the cell.
  # example usage:
  # ly = pya.Application.instance().main_window().current_view().active_cellview().layout() 
  # pcell = ly.create_cell("Waveguide_Bend", "SiEPIC", { } )
  # find_PCell_pins( pcell )
  
  print(LayerPinRec)
  LayerPinRecN = LayerPinRec #subcell.layout().layer(LayerPinRec)
  iter2 = subcell.begin_shapes_rec(LayerPinRecN)
  pins = {} # dictionary for pin information
  while not(iter2.at_end()):
    # Find text label for PinRec, to get the port numbers
    if iter2.shape().is_text():
      texto= iter2.shape().text.transformed(iter2.itrans())
      x = texto.x
      y = texto.y
      text = iter2.shape().text
      print( "PinRec label: %s at (%s, %s)" % (text, x, y) )
      pins[ str(text.string) + "_x" ] = x
      pins[ str(text.string) + "_y" ] = y
    iter2.next()

  return pins
  
Example_mixed_waveguide_types()
