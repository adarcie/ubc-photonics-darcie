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
  sepx1=400
  sepy=400
  
  gc_xoffset=100
  spiral_y_offset=-50
  
  print("start")
  
  min_bend_radius=10
  

  # parameter definitions
  taper_length = 10
  wg_width1 = 0.5
  wg_width2 = 3.0
  
  num_rows=5
  num_cols=15
  
  num_rows=2
  num_cols=2
  
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
  LayerPinRec = cell.layout().layer(TECHNOLOGY['PinRec'])
    
  # Create a sub-cell for our layout, place the cell in the top cell
  top_cell = cell
  cell = cell.layout().create_cell("spiral_sweep_cell_v2")
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
  top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))
  
  for row in range(num_rows):
    for col in range(num_cols):

      print("EBeam.spiral_sweep")
      
      
      spiral_length=1200*col
      spiral_spacing=1*row+1
      
      newcellname="spirals_"+str(spiral_length)+"_"+str(spiral_spacing)
      delete_cell = ly.cell(newcellname)
      if delete_cell:
        ly.delete_cell(delete_cell.cell_index())
      spiral_cell = ly.create_cell(newcellname)
      
      
      #place loss structure and get actual length
      with Capturing() as output:
        cell_spiral = ly.create_cell("Spiral", "EBeam-dev", 
          {"length":spiral_length,"wg_width":0.5,"min_radius":10,"wg_spacing":spiral_spacing,"spiral_ports":1})
        #determine size of spiral and set additional GC offset
        w=cell_spiral.bbox().width()
        h=cell_spiral.bbox().height()
        add_GC_offset=h/2*dbu#use height since cell is rotated
        sepx=add_GC_offset+sepx1
          
        t = Trans(Trans.R270, col*sepx/dbu, (row*sepy+75+spiral_y_offset)/dbu)
        spiral_cell.insert(CellInstArray(cell_spiral.cell_index(), t))
      print('output:', output)
      matching = [s for s in output if "spiral length" in s]
      real_length=float(matching[0].split("length: ")[1].split(" mic")[0])
      
      #determine pin locations for GC routing
      pin_locs=find_PCell_pins(spiral_cell,LayerPinRec)
      print(pin_locs)
      scalefac=dbu
      pin1x=float(pin_locs['pin1_x'])*scalefac
      pin1y=float(pin_locs['pin1_y'])*scalefac
      print(pin1y)
      pin2x=float(pin_locs['pin2_x'])*scalefac
      pin2y=float(pin_locs['pin2_y'])*scalefac
      
      
      
      # place grating couplers
      cell_taper = ly.cell("1550_220_gc_new").cell_index()
      t = Trans(Trans.R0, (col*sepx-gc_xoffset-add_GC_offset)/dbu, row*sepy/dbu)
      spiral_cell.insert(CellInstArray(cell_taper, t))
      t = Trans(Trans.R0, (col*sepx-gc_xoffset-add_GC_offset)/dbu, row*sepy/dbu+127/dbu)
      spiral_cell.insert(CellInstArray(cell_taper, t))
      
      
      #route top waveguide to pin1
      print(row*sepy+127-pin1y,min_bend_radius)
      if ((row*sepy+127)-pin1y)<2*min_bend_radius:#add extra bump to ensure min bend radius
        dpath = DPath([DPoint(col*sepx-gc_xoffset-add_GC_offset,row*sepy+127),DPoint(col*sepx-gc_xoffset+min_bend_radius-add_GC_offset,row*sepy+127),DPoint(col*sepx-gc_xoffset+min_bend_radius-add_GC_offset,row*sepy+127+max([2*min_bend_radius,2*min_bend_radius-(row*sepy+127-pin1y)])),DPoint(col*sepx-10,row*sepy+127+max([2*min_bend_radius,2*min_bend_radius-(row*sepy+127-pin1y)])), DPoint(col*sepx-10,pin1y),DPoint(pin1x,pin1y)], 0.5)
        spiral_cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        print("extending range")
        top_ylength1=abs((row*sepy+127)-(row*sepy+127+max([2*min_bend_radius,2*min_bend_radius-(row*sepy+127-pin1y)])))
        top_ylength2=abs(pin1y-(row*sepy+127+max([2*min_bend_radius,2*min_bend_radius-(row*sepy+127-pin1y)])))
        top_ylength=top_ylength1+top_ylength2
      
      else:
        dpath = DPath([DPoint(col*sepx-gc_xoffset-add_GC_offset,row*sepy+127),DPoint(col*sepx-10,row*sepy+127), DPoint(col*sepx-10,pin1y),DPoint(pin1x,pin1y)], 0.5)
        spiral_cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        top_ylength=abs(row*sepy+127-(pin1y))
        
                
        
      #route bottom waveguide to pin2
      dpath = DPath([DPoint(col*sepx-gc_xoffset-add_GC_offset,row*sepy),DPoint(col*sepx-gc_xoffset+min_bend_radius*2-add_GC_offset,row*sepy), DPoint(col*sepx-gc_xoffset+min_bend_radius*2-add_GC_offset,pin2y),DPoint(pin2x,pin2y)], 0.5)
      spiral_cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
      bottom_ylength=abs(row*sepy-pin2y)
      path_to_waveguide(cell = spiral_cell, verbose=True, params = 
        {'width': wg_width1, 'adiabatic': True, 'radius': min_bend_radius, 'bezier': 0.2, 
        'wgs': [{'width': wg_width1, 'layer': 'Si', 'offset': 0.0}]})
        
      #add routing WGs to total length (STRAIGHT APPROX - bends should cancel anyway)
      real_length+=2*gc_xoffset+2*add_GC_offset+top_ylength+bottom_ylength
        
    # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
      t = pya.Trans(Trans.R0,(col*sepx-gc_xoffset-add_GC_offset)/dbu, (row*sepy+127)/dbu)
      text = pya.Text ("opt_in_TE_1550_device_spiral_loss_length_"+str(round(real_length))+"um_spacing_"+str(round(spiral_spacing*1000))+"nm", t)
      shape = spiral_cell.shapes(TextLayerN).insert(text)
      shape.text_size = 10*dbu
      
      
      
      cell.insert(CellInstArray(spiral_cell.cell_index(), Trans.R0))
      
    
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
