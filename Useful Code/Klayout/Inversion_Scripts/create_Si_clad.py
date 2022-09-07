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

  p = pya.AbsoluteProgress("Create_Cladding")
  p.format_unit = 7

  # Create new layers for the inverted layout: one high resolution, and one low resolution
  layer_in=layout.layer(pya.LayerInfo(1,0))
  layer_clad = layout.layer(pya.LayerInfo(1, 2))
  
  # Create a new cell
  newcellname="cladding_layer"
  delete_cell = layout.cell(newcellname)
  if delete_cell:
    layout.delete_cell(delete_cell.cell_index())
  cell = layout.create_cell(newcellname)

  if OUT_MODE == 1:

      # perform sizing operations:  http://www.klayout.de/doc-qt4/code/class_Polygon.html
      # 1000 nm
      shapes_clad = cell.shapes(layer_clad)
      pya.ShapeProcessor().size(layout,topcell,layer_in,shapes_clad,2000,pya.EdgeProcessor.ModeOr,True,True,True)# bias pattern up
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
