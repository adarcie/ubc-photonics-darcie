
# Enter your Python code here

from pya import *
  
# Import functions from SiEPIC-Tools, and get technology details
from SiEPIC.utils import select_paths, get_layout_variables
TECHNOLOGY, lv, ly, cell = get_layout_variables()
dbu = ly.dbu
from SiEPIC.extend import to_itype
from SiEPIC.scripts import path_to_waveguide
import glob,os
import random




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
  
  TECHNOLOGY, lv, ly, cell = get_layout_variables()
  TextLayerN = cell.layout().layer(TECHNOLOGY['Text'])
  SEMLayer = cell.layout().layer(TECHNOLOGY['SEM'])
  Hireslayer = cell.layout().layer(TECHNOLOGY['31_Si_p6nm'])
  
  # clean all cells within the present cell
  ly.prune_subcells(cell.cell_index(), 10)


  p = pya.AbsoluteProgress("Layout invert resist tone")
  p.format_unit = 7

  # Create new layers for the inverted layout: one high resolution, and one low resolution
  layer_high = layout.layer(pya.LayerInfo(103, 0))
  layer_in=layout.layer(pya.LayerInfo(1,0))
  layer_temp = layout.layer(pya.LayerInfo(300, 0))
  layer_tile = layout.layer(pya.LayerInfo(400, 0))
  
  
  # Create a new cell
  newcellname="text_labels_buffer1"
  delete_cell = layout.cell(newcellname)
  if delete_cell:
    layout.delete_cell(delete_cell.cell_index())
  text_cell = layout.create_cell(newcellname)
  
  
  
  # set up vertical array of buffer distances (um)
  yspacing=200
  buffer_list=[2,3,4,5,6,7,8,9,10]#,10]#,15]#,20]#,]
  random.shuffle(buffer_list)#[::-1]
  print(buffer_list)
  
  #set up horizontal array of densities
  density_list=[0,.01,0.02,0.03,0.05,0.07,0.08,0.1,0.125,0.15,0.2,0.3,.4,0.5,.6,0.8]
  random.shuffle(density_list)#[::-1]
  print(density_list)
  
  
  startx=0
  endx=150
  xspacing=endx
  y_offset=50-12+50+33.2-5-13
  x_offset=65-40+50-25.6+0.7+0.5*(xspacing-100)
  
  xlabel_orig=59.6+5.4-5.04-8.2+0.7+0.5*(xspacing-100)
  ylabel_orig=178.5-1.5+0.766+2-13
  num_x_coords=len(density_list)
  ring_radius=30
  annulus_width=15

  SEMsizex=10
  SEMsizey=10
  SEM_offsetx=endx/2+ring_radius-3-SEMsizex/2
  SEM_offsety=yspacing/2+7
  
    
    
  #create array of given device
  #cell_dev= ly.create_cell("PCM_Ring").cell_index()
#  cell_dev=layout.cell("Ring_Jaspreet").cell_index()
  cell_dev=layout.cell("base_ring").cell_index()
  #topcell.insert(pya.CellInstArray(

  tilingcells=[]
  for i in range(len(buffer_list)):
    
    # Create a new cell for each buffer size
    newcellname="tiling_buffer"+str(round(buffer_list[i]*1000))+"nm"
    delete_cell = layout.cell(newcellname)
    if delete_cell:
      layout.delete_cell(delete_cell.cell_index())
    tilingcells.append(layout.create_cell(newcellname))
    tilingcell=tilingcells[i]
      
    for j in range(num_x_coords):
      t = pya.Trans(Trans.R0,(xlabel_orig+j*(endx-startx))/dbu, (ylabel_orig+i*yspacing)/dbu)
      text = pya.Text ("opt_in_TE_1550_device_buffer"+str(round(buffer_list[i]*1000))+"nm&density"+str(round(density_list[j]*100))+"&col"+str(j)+"&row"+str(i)+"&norm", t)
      shape = text_cell.shapes(TextLayerN).insert(text)
      text.size=10
      t = Trans(Trans.R0, (x_offset+j*(endx-startx))/dbu, (y_offset+i*yspacing)/dbu)
      tilingcell.insert(CellInstArray(cell_dev, t))
    

  #create tiling array
  absminx=startx
  absminy=y_offset
  absmaxx=startx
  absmaxy=y_offset
  for n in range(len(buffer_list)):
  
    
    tilingcell=tilingcells[n]
    print("Buffer:",str(buffer_list[n]))
    print(tilingcell)
    layer_tile = layout.layer(pya.LayerInfo(400, 0))
    
    mindistance=buffer_list[n]*1000#distance between pattern and nearest tiles (nm > 10)
    #make tiles

    starty=n*yspacing
    endy=yspacing*(n+1)
  
    y0=starty+yspacing/2
    
    for densind in range(num_x_coords):
      x=startx+xspacing*densind
      x0=startx+xspacing/2+xspacing*densind
      y=starty
      
      #ADD SEM BOX
      topcell.shapes(SEMLayer).insert(pya.DBox(0,0,SEMsizex,SEMsizey).moved(x+SEM_offsetx, y+SEM_offsety))
      
      #fill per 100um box
      boxsize=1#um
      density=density_list[densind]
      xsize=(density*boxsize**2)**0.5
      ysize=(density*boxsize**2)**0.5
      density=density_list[densind]
      while x<endx+xspacing*densind:
        y=starty
        while y<endy:
          #get relative position of x and y
          xrel=x-x0
          yrel=y-y0
          
          #track maximum and minimum x,y positions for use later
          if x<absminx:
            absminx=x
          if x>absmaxx:
            absmaxx=x
          if y<absminy:
            absminy=y
          if y>absmaxy:
            absmaxy=y
          
          #create tile annulus
          if (xrel**2+yrel**2<=(ring_radius+annulus_width)**2) and (xrel**2+yrel**2>=(ring_radius-annulus_width)**2):
            tilingcell.shapes(layer_tile).insert(pya.Box(x/dbu, y/dbu, (x+xsize)/dbu, (y+ysize)/dbu))
          y=y+boxsize
        x=x+boxsize
        
    # perform sizing operations:  http://www.klayout.de/doc-qt4/code/class_Polygon.html
    # 1000 nm
    shapes_high = tilingcell.shapes(layer_high)
    shapes_temp = tilingcell.shapes(layer_temp)
    shapes_tile=tilingcell.shapes(layer_tile)
    shapes_in=tilingcell.shapes(layer_in)
    shapes_hires=tilingcell.shapes(Hireslayer)
    print(mindistance)
    pya.ShapeProcessor().size(layout,tilingcell,layer_in,shapes_high,mindistance-10,pya.EdgeProcessor.ModeOr,True,True,True)
    p.inc
    pya.ShapeProcessor().size(layout,tilingcell,layer_high, shapes_temp, 10,pya.EdgeProcessor.ModeAnd,True,True,True)
    p.inc
    #shapes_high.clear()
    #pya.ShapeProcessor().boolean(layout,cell,layer_temp,layout,topcell,layer_in,shapes_high,pya.EdgeProcessor.ModeXor,True,True,True)
    pya.ShapeProcessor().boolean(layout,tilingcell,layer_tile,layout,tilingcell,layer_temp,shapes_tile,pya.EdgeProcessor.ModeANotB,True,True,True)
    layer_tile=layer_tile-layer_temp
    p.inc
    
    #put tiling shapes on hires layer (CHANGE DEPENDING ON PROCESS)
    shapes_hires.insert(shapes_tile)
    
    topcell.insert(pya.CellInstArray(tilingcell.cell_index(), pya.Trans(0, 0)))
    
  #insert text cell
  topcell.insert(pya.CellInstArray(text_cell.cell_index(), pya.Trans(0, 0)))
    
  #create cell for alignment structures
  #newcellname="alignment_GCs"
  #delete_cell = layout.cell(newcellname)
  #if delete_cell:
  #  layout.delete_cell(delete_cell.cell_index())
  #align_cell = layout.create_cell(newcellname)
    
  alignbuffer=100
  #summarize coordinates of corner GCs and labels
  align_labels=["topright","topleft","botleft","botright"]
  align_xcoords=[absmaxx+alignbuffer,absminx-alignbuffer,absminx-alignbuffer,absmaxx+alignbuffer]
  align_ycoords=[absmaxy+alignbuffer,absmaxy+alignbuffer,absminy-alignbuffer,absminy-alignbuffer]
  cell_GC = ly.create_cell("ebeam_gc_te1550", "EBeam").cell_index()
  
  for align_ind in range(len(align_labels)):
    alignx=align_xcoords[align_ind]
    aligny=align_ycoords[align_ind]
    
    #place GCs
    t = Trans(Trans.R0, alignx/dbu, aligny/dbu)
    cell.insert(CellInstArray(cell_GC, t))
    t = Trans(Trans.R0, alignx/dbu, (aligny-127)/dbu)
    cell.insert(CellInstArray(cell_GC, t))
    
    #route waveguides
    dpath = DPath([DPoint(alignx,aligny), DPoint(alignx+10,aligny), DPoint(alignx+10,aligny-127),DPoint(alignx,aligny-127)], 0.5)
    cell.shapes(layer_in).insert(dpath.to_itype(dbu))
    
    #text labels
    t = pya.Trans(Trans.R0,(alignx)/dbu, (aligny)/dbu)
    text = pya.Text ("opt_in_TE_1550_device_ring30um&densitytest&"+align_labels[align_ind], t)
    shape = cell.shapes(TextLayerN).insert(text)
      
  path_to_waveguide(cell = cell, verbose=True, params = 
        {'width': 0.5, 'adiabatic': True, 'radius': 10.0, 'bezier': 0.2, 
        'wgs': [{'width': 0.5, 'layer': 'Si', 'offset': 0.0}]})  
  p.destroy
  
  
    


#run function


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
