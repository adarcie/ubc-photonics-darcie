##Supports multithreading
# - calculate area by section, thread each section separately

import pya

pixel_size_x = 100
pixel_size_y = 227


threads = 4

ly = pya.CellView.active().layout()
# takes density from layer 100
li = ly.layer(400, 0)
si = ly.top_cell().begin_shapes_rec(li)

tp = pya.TilingProcessor()

# this example uses an image for output
img = pya.Image()

tp.tile_size(pixel_size_x, pixel_size_y)
tp.output("res", img)
tp.input("input", si)
tp.dbu = ly.dbu
tp.threads = threads
# inside tiling processor compute the density and output to the image
tp.queue("_tile && (var d = to_f(input.area(_tile.bbox)) / to_f(_tile.bbox.area);_output(res, d))")
tp.execute("Density map")

# place the image into the view - it's already properly configured by the 
# tiling processor
# you could use the "data mapping" feature of the images for creating a heat map
# for example.
print(img)
pya.LayoutView.current().insert_image(img)



with open(r"C:\Users\adam\Downloads\densitymap.txt", mode = 'w') as f:
    f.write(str(img))
