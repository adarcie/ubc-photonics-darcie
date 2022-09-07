import pya



'''
Resist types:

- Negative tone, e.g., HSQ
  Shapes drawn in the layout become silicon; everything else is etched
  Waveguide layer is thus the solid waveguide core
  
- Postive tone, e.g., ZEP, PMMA
  Shapes drawn in the layout get etched; everything else remains as silicon
  Waveguides drawn by creating trenches (cladding) rather than the core
  Less convenient for waveguides
  Excellent for photonic crystals (holes)
  
  OUT_MODE = # 1=one layer, 2=two layers
  
'''

def layout_invert_resist_tone(self):

  topcell = self
  layout = self.layout()

  p = pya.AbsoluteProgress("Biasing")
  p.format_unit = 7

  # Create new layers for the inverted layout: one high resolution, and one low resolution
  layer_high = layout.layer(pya.LayerInfo(100, 0))
  layer_in=layout.layer(pya.LayerInfo(1,0))
  layer_temp = layout.layer(pya.LayerInfo(300, 0))


  layer_tile = layout.layer(pya.LayerInfo(400, 0))
  
  # Create a new cell
  newcellname="bias_tone"
  delete_cell = layout.cell(newcellname)
  if delete_cell:
    layout.delete_cell(delete_cell.cell_index())
  cell = layout.create_cell(newcellname)
  
    
    
    
  shapes_high = cell.shapes(layer_high)
  shapes_temp = cell.shapes(layer_temp)
  shapes_tile=cell.shapes(layer_tile)
  shapes_in=cell.shapes(layer_in)

  #fill per 100um box
  boxsize=100
  
  startx=0
  endx=150
  dx=5
  
  
  dy=2
    
  
  x=startx
  bias_nm=150
  while x<endx:
    
    bias_nm=bias_nm+100
    y=-1
    
    
    
    #"place" region that will be re-sized
    cell.shapes(layer_tile).insert(pya.Box(x/dbu, y/dbu, (x+dx)/dbu, (y+dy)/dbu))
        
    # perform sizing operations:  http://www.klayout.de/doc-qt4/code/class_Polygon.html
    # 1000 nm
  
  
    #create temp shape along layer_in only where it is within layer_tile
    pya.ShapeProcessor().boolean(layout,cell,layer_tile,layout,topcell,layer_in,shapes_temp,pya.EdgeProcessor.ModeAnd,True,True,True)
    p.inc
  
    
    #bias layer_temp onto shapes_high
    pya.ShapeProcessor().size(layout,cell,layer_temp,shapes_temp,bias_nm,pya.EdgeProcessor.ModeOr,True,True,True)
    p.inc
    
    #move contents of layer_temp onto layer_high to be saved
    shapes_high.insert(shapes_temp)
    
    
    #remove temporary shapes
    shapes_tile.clear()
    
    
    x=x+dx
    
    
  topcell.insert(pya.CellInstArray(cell.cell_index(), pya.Trans(0, 0)))
  p.destroy

pya.Cell.layout_invert_resist_tone = layout_invert_resist_tone


lv = pya.Application.instance().main_window().current_view()
if lv == None:
  raise Exception("No view selected")
ly = lv.active_cellview().layout() 
if ly == None:
  raise Exception("No active layout")
cell = lv.active_cellview().cell
if cell == None:
  raise Exception("No active cell")


cell.layout_invert_resist_tone()
lv.add_missing_layers()
