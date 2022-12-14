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

  OUT_MODE = 1 # 1=one layer, 2=two layers

  topcell = self
  layout = self.layout()

  p = pya.AbsoluteProgress("Layout invert resist tone")
  p.format_unit = 7

  # Create new layers for the inverted layout: one high resolution, and one low resolution
  layer_high = layout.layer(pya.LayerInfo(100, 0))
  layer_low = layout.layer(pya.LayerInfo(101, 0))
  layer_in=layout.layer(pya.LayerInfo(1,0))
  layer_temp = layout.layer(pya.LayerInfo(300, 0))
  layer_temp2 = layout.layer(pya.LayerInfo(301, 0))
  
  # Create a new cell
  newcellname="invert_resist_tone"
  delete_cell = layout.cell(newcellname)
  if delete_cell:
    layout.delete_cell(delete_cell.cell_index())
  cell = layout.create_cell(newcellname)

  if OUT_MODE == 2:
    
      # perform sizing operations:  http://www.klayout.de/doc-qt4/code/class_Polygon.html
      # 1) high = in sized(0.1):f what will be come the high resolution trench
      #    high = high - in
      # 100 nm
      shapes_high = cell.shapes(layer_high)
      shapes_temp = cell.shapes(layer_temp)
      pya.ShapeProcessor().size(layout,topcell,layer_in,shapes_high,150,pya.EdgeProcessor.ModeOr,True,True,True)
      p.inc
      pya.ShapeProcessor().size(layout,cell,layer_high, shapes_temp, 1,pya.EdgeProcessor.ModeAnd,True,True,True)
      p.inc
      shapes_high.clear()
      pya.ShapeProcessor().boolean(layout,cell,layer_temp,layout,topcell,layer_in,shapes_high,pya.EdgeProcessor.ModeXor,True,True,True)
      p.inc
    
      # 2) low = in sized(1): what will become the low resolution trench
      #    low = low - high(temp) - in
      # 1000 nm
      shapes_temp2 = cell.shapes(layer_temp2)
      pya.ShapeProcessor().merge(layout,topcell,layer_in,shapes_temp2,True,1,True,True)
      p.inc
      shapes_low = cell.shapes(layer_low)
      pya.ShapeProcessor().size(layout,cell,layer_temp2,shapes_low,1999,pya.EdgeProcessor.ModeAnd,True,True,True)
      p.inc
      pya.ShapeProcessor().boolean(layout,cell,layer_low, layout,cell,layer_temp,shapes_temp2,pya.EdgeProcessor.ModeANotB,True,True,True)
      p.inc
      shapes_low.clear()
      shapes_temp.clear()
      pya.ShapeProcessor().boolean(layout,cell,layer_temp2,layout,topcell,layer_in,shapes_low,pya.EdgeProcessor.ModeANotB,True,True,True)
      p.inc
      shapes_temp2.clear()

  if OUT_MODE == 1:

      # perform sizing operations:  http://www.klayout.de/doc-qt4/code/class_Polygon.html
      # 1000 nm
      shapes_high = cell.shapes(layer_high)
      shapes_temp = cell.shapes(layer_temp)
      pya.ShapeProcessor().size(layout,topcell,layer_in,shapes_high,2001,pya.EdgeProcessor.ModeOr,True,True,True)
      p.inc
      pya.ShapeProcessor().size(layout,cell,layer_high, shapes_temp, 1,pya.EdgeProcessor.ModeAnd,True,True,True)
      p.inc
      shapes_high.clear()
      pya.ShapeProcessor().boolean(layout,cell,layer_temp,layout,topcell,layer_in,shapes_high,pya.EdgeProcessor.ModeXor,True,True,True)
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
