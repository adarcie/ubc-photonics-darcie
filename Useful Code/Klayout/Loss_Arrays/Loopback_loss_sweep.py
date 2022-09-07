''' Author: Stephen

KNOWN BUG: The path_to_waveguide function has to be called twice to convert all the paths. If called once it will alternate between odd and even rows. Could not figure out the exact cause
I suspect it has something to do with the way exceptions are raised or that the GUI interupts the script.
'''
from pya import *



# Example layout function
def pc_gc_pair(  a,x,y,r,vertices,positive,apodized,feature_size,taper_length,wg_width,name,xloc,yloc):

  # Create a layout using different waveguide types.
  # uses:
  #  - the SiEPIC EBeam Library
  # creates the layout in the presently selected cell
  # deletes everything first

  # parameter definitions

  wg_width1 = 0.5#wg_width
  wg_width2 = a*(y-4)

  print("EBeam.Example_mixed_waveguide_types")

  # Import functions from SiEPIC-Tools, and get technology details
  from SiEPIC.utils import select_paths, get_layout_variables
  TECHNOLOGY, lv, ly, cell = get_layout_variables()
  dbu = ly.dbu
  from SiEPIC.extend import to_itype
  from SiEPIC.scripts import path_to_waveguide
  
  #clean all cells within the present cell
  ly.prune_subcells(cell.cell_index(), 10)

  
  # Layer mapping:
  LayerSiN = ly.layer(TECHNOLOGY['Waveguide'])
  TextLayerN = cell.layout().layer(TECHNOLOGY['Text'])
    
  # Create a sub-cell for our layout, place the cell in the top cell
  top_cell = cell.layout().top_cell()
  cell = cell.layout().create_cell("gcs"+str(xloc)+str(yloc))
  t = Trans(Trans.R0, yloc / dbu, yloc / dbu)
  top_cell.insert(CellInstArray(cell.cell_index(),t))
  t = Trans(Trans.R0, xloc / dbu, (yloc+127) / dbu)
  top_cell.insert(CellInstArray(cell.cell_index(),t))
  
  # Import cells from the SiEPIC Library, and instantiate them
  
  # taper, from waveguide1 to waveguide2
  cell_taper = ly.create_cell("ebeam_taper_te1550", "EBeam", 
    {"wg_width1":wg_width1,"wg_width2":wg_width2, "wg_length":taper_length}
    ).cell_index()
    
  # place tapers  
  t = Trans(Trans.R0, xloc/dbu, yloc/dbu)
  cell.insert(CellInstArray(cell_taper, t))
  t = Trans(Trans.R0, xloc/dbu, (yloc+127)/dbu)
  cell.insert(CellInstArray(cell_taper, t))
    
  pcell = ly.create_cell("PhC gc, with hexagon cell","EBeam-dev", {"a":a,"x":x,"y":y,"r":r, "vertices":vertices, "positive":positive, "apodized":apodized,"feature_size":feature_size,"layer":TECHNOLOGY['31_Si_p6nm']} ).cell_index()
  #"﻿PhC gc, with hexagon cell", "EBeam - dev", {"a":0.231,"x":50,"y":60,"r": 0.073, "vertices": 64, "positive": 0, "apodized": 0 } ).cell_index()


  t = Trans(Trans.R180, (taper_length+a*((x-4)/2))/dbu, 0/dbu)  
  cell.insert(CellInstArray(pcell, t ))
  
  # finish up, unselect, zoom, show all hierarchy 
  lv.clear_object_selection()
  lv.zoom_fit()
  lv.max_hier()

ymax=1
ymin=0  
xmax=1
xmin=0
for y in range(ymin,ymax):
    #a=0.178+0.004*y#1220
    #a=0.186+0.004*y#1280
    #a=0.231#+0.004*y#1550
    #a=0.237+0.004*y#1626
    #a=0.191+0.004*y#1310
    
    #from last run
    #a=0.235+0.004*y#1550
    #a=0.237+0.004*y#1625
    #a=0.182+0.004*y#1310
    #a=0.178+0.004*y#1280
    a=0.243#1220
    #t=120-y*2
    t=70
    
    for x in range(xmin,xmax):
        #r=0.0655#+0.004*x#1550
        #r=0.0748+0.004*x#1626
        #t=100+x*5+y*5
        #r=0.056+0.004*x#1220
        #r=0.059+0.004*x#1280
        #r=0.0602+0.004*x#1310
        
        #from last run
        #r=0.0535+0.004*x#1550
        #r=0.0628+0.004*x#1625
        #r=0.047+0.004*x#1310
        #r=0.051+0.004*x#1280
        r=0.0735#1220
        #x=0.064*2900/1550
        
        #r=0.0535#1550  
        #a=0.235 #1550 
        #t=t-x*2
        pc_gc_pair(a=a,x=78,y=50,r=r,vertices=16,positive=1,apodized=0,feature_size=0.08,taper_length=t,wg_width=0.5,name="",xloc=180*x,yloc=157*y)

# pc_gc_pair(a=0.235,x=78,y=50,r=0.0535,vertices=32,positive=1,apodized=0,feature_size=0.06,taper_length=120,wg_width=0.5,name="top_left",x_location=180*(xmax+2),y_location=157*(ymin-3))
#pc_gc_pair(a=0.235,x=78,y=50,r=0.0535,vertices=32,positive=1,apodized=0,feature_size=0.06,taper_length=120,wg_width=0.5,name="top_right",x_location=180*(xmax+2),y_location=157*(ymax+2))
#pc_gc_pair(a=0.235,x=78,y=50,r=0.0535,vertices=32,positive=1,apodized=0,feature_size=0.06,taper_length=120,wg_width=0.5,name="bottom_left",x_location=180*(xmin-3),y_location=157*(ymin-3))
#pc_gc_pair(a=0.235,x=78,y=50,r=0.0535,vertices=32,positive=1,apodized=0,feature_size=0.06,taper_length=120,wg_width=0.5,name="bottom_right",x_location=180*(xmin-3),y_location=157*(ymax+2))
#
