
# Enter your Python code here

from pya import *
  
# Import functions from SiEPIC-Tools, and get technology details
from SiEPIC.utils import select_paths, get_layout_variables
TECHNOLOGY, lv, ly, cell = get_layout_variables()
dbu = ly.dbu
from SiEPIC.extend import to_itype
from SiEPIC.scripts import path_to_waveguide
import glob,os

# Layer mapping:
LayerSiN = ly.layer(TECHNOLOGY['Waveguide'])
TextLayerN = cell.layout().layer(TECHNOLOGY['Text'])
  
# Create a sub-cell for our layout, place the cell in the top cell
top_cell = cell
cell = cell.layout().create_cell("text_array_rightvert")
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)
top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))


startx=3000
starty=0

base_name="opt_in_TE_1550_device_sec1_rightvert_density_"

nrows=13
ncols=1

#spacing between rows
xrow=0
yrow=227

#spacing between columns
xcol=0
ycol=0

densitylist=[1,2,3,4,5,7,10,20,30,35,40,45,50]


x=startx
y=starty
#generate new text labels
for i in range(nrows):
  x=startx+i*xrow
  y=starty+i*yrow
  for j in range(ncols):
    x=x+xcol
    y=y+ycol
  
    t = Trans(Trans.R0, x/dbu, y/dbu)
    text = pya.Text (base_name+str(densitylist[i]),t)
    shape = cell.shapes(TextLayerN).insert(text)
    shape.text_size = 3/dbu