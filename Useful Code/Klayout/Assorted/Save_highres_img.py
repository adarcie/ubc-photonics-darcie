
# Enter your Python code here

from pya import *
lv = pya.LayoutView.current()
ly = pya.CellView.active().layout()

# top cell bounding box in micrometer units
bbox = ly.top_cell().dbbox()

# compute an image size having the same aspect ratio than 
# the bounding box
w = 3e3
h = int(0.5 + w * bbox.height() / bbox.width())

lv.save_image_with_options('E:\\NEXTCLOUD_NEW\\Lab data\\Adam\\Future_Density_Tests\\GC_Separated_From_Block\\highres_img.png', w, h, 0, 0, 0, bbox, True)