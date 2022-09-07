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

  p = pya.AbsoluteProgress("Layout invert resist tone")
  p.format_unit = 7

  # Create new layers for the inverted layout: one high resolution, and one low resolution
  layer_high = layout.layer(pya.LayerInfo(100, 0))
  layer_in=layout.layer(pya.LayerInfo(1,0))
  layer_temp = layout.layer(pya.LayerInfo(300, 0))

  
  layer_tile = layout.layer(pya.LayerInfo(400, 0))
  
  # Create a new cell
  newcellname="invert_resist_tone"
  delete_cell = layout.cell(newcellname)
  if delete_cell:
    layout.delete_cell(delete_cell.cell_index())
  cell = layout.create_cell(newcellname)
  
    
  #make tiles
  mindistance=3000 #distance between pattern and nearest tiles (nm > 200)
  density=0.5

  startx=0
  endx=4500
  starty=0
  endy=1800
  
  #fill per 100um box
  boxsize=100
  xsize=(density*boxsize**2)**0.5
  ysize=(density*boxsize**2)**0.5
  
  x=startx
  y=starty
  while x<endx:
    y=starty
    while y<endy:
      cell.shapes(layer_tile).insert(pya.Box(x/dbu, y/dbu, (x+xsize)/dbu, (y+ysize)/dbu))
      y=y+boxsize
    x=x+boxsize

  
  


  # perform sizing operations:  http://www.klayout.de/doc-qt4/code/class_Polygon.html
  # 1000 nm
  shapes_high = cell.shapes(layer_high)
  shapes_temp = cell.shapes(layer_temp)
  shapes_tile=cell.shapes(layer_tile)
  pya.ShapeProcessor().size(layout,topcell,layer_in,shapes_high,mindistance-200,pya.EdgeProcessor.ModeOr,True,True,True)
  p.inc
  pya.ShapeProcessor().size(layout,cell,layer_high, shapes_temp, 200,pya.EdgeProcessor.ModeAnd,True,True,True)
  p.inc
  shapes_high.clear()
  #pya.ShapeProcessor().boolean(layout,cell,layer_temp,layout,topcell,layer_in,shapes_high,pya.EdgeProcessor.ModeXor,True,True,True)
  pya.ShapeProcessor().boolean(layout,cell,layer_tile,layout,cell,layer_temp,shapes_tile,pya.EdgeProcessor.ModeANotB,True,True,True)
  
  layer_tile=layer_tile-layer_temp
  
  p.inc
    
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
