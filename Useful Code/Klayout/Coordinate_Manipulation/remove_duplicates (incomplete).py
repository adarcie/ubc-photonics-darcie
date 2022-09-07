
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
cell = cell.layout().create_cell("array_text")

top_cell.insert(CellInstArray(cell.cell_index(), Trans.R0))
#  t = Trans(Trans.R0, 0 / dbu, 0 / dbu)

#Import coordinate file as text and create rows

os.chdir("D:\\Nextcloud\\Tight Spirals Base Dose Sweep")


coords_file='spiral_row_coords.txt'
#coords_file='SINGLE_coords_alignment.txt'

text_file=open(coords_file)
lines=text_file.read().split('\n')
text_file.close

coordsx=[]
coordsy=[]
namelist=[]
for i in range(4,len(lines)-5):
    row=lines[i].split(", ")
    print(row)
    coordsx.append(float(row[0]))
    coordsy.append(float(row[1]))
    name=row[2]
    for n in range(3,len(row)):
        name=name+'_'+row[n]
    name=name+"_"+str(i)
    namelist.append(name)

print(namelist)
numrows=7
numcols=1
spacingy=1000
spacingx=0


newx=[]
newy=[]
newnames=[]
for i in range(numrows):
  for j in range(numcols):
    for n in range(len(namelist)):
        if i!=-1:
          newy.append(coordsy[n]+spacingy*i)
          newx.append(coordsx[n]+spacingx*j)
          newnames.append(namelist[n]+"_col1_row"+str(i+1))
          #newnames.append(namelist[n]+"_row"+str(i+1)+"_col"+str(j+1))
        
print(newnames)

#generate new text labels
for i in range(len(newnames)):
  t = Trans(Trans.R0, newx[i]/dbu, newy[i]/dbu)
  text = pya.Text ("opt_in_"+newnames[i],t)
  text.size=100
  shape = cell.shapes(TextLayerN).insert(text)