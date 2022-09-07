  # SiEPIC-Tools scripted layout benchmark
  #
  # Create a complete layout for parameter sweeping contra-directional couplers
  # usage:
  #  - the SiEPIC EBeam Library
  # Modify parameters in layout_parameters() function to create a parameter sweep on selected contra-DC parameter.
  # 
  # Script will generate an array of the devices with the selected parameters, and generate GCs for testing with automated measurement labels
  # and finally generate interleaved waveguide routes between GCs and devices for compact routing
  #
  # Author:       Mustafa Hammood 
  #                   Mustafa@ece.ubc.ca
  # September 2018

  # Uncomment path_to_waveguide to convert everything to waveguides, or just do it on your own from SiEPIC Tools menu.
  
  
# Import KLayout-Python API
from pya import *


# linspace function without using numpy, because why not?
def linspace_without_numpy(low, up, length):
    step = ((up-low) * 1.0 / length)
    return [low+i*step for i in range(length)]
    
# define layout parameters in the class below
# ALL distance parameters are in microns unless specified otherwise
class parameters():
  # parameter to sweep
  
  
  # number of devices (i.e. length of this array) MUST BE EVEN as this is interleaved routing configuration!
  Num_sweep = 20

  # contraDC device parameters (refer to PCell definition)
  N =  linspace_without_numpy(100,1500,Num_sweep)
  period = linspace_without_numpy(.318,.318,Num_sweep)
  g = linspace_without_numpy(.22,.22,Num_sweep)
  w1 = linspace_without_numpy(.56,.56,Num_sweep)
  w2 = linspace_without_numpy(.44,.44,Num_sweep)
  dW1 = linspace_without_numpy(.05,.05,Num_sweep)
  dW2 = linspace_without_numpy(.03,.03,Num_sweep)
  sine = 0
  a = linspace_without_numpy(0,0,Num_sweep)
  
  # routing and device placement parameters
  
  sbend_L = 13
  sbend_R = 14
  sbend_H = 3
  
  x_offset = 150              # spacing between grating couplers columns
  wg_bend_radius = 10    # waveguide routes bend radius
  bezier = 1                   # Use adiabatic bezier bends (if 1)
  bezier_N = 0.2            # Bezier bend parameter
  device_spacing = 7.3   # spacing between devices
  wg_width = .5          # waveguide routes width
  taper_L = sbend_L     # keep this relation!
  GC_pitch = 127         # spacing between grating couplers array (for a single device)
  
  wg_pitch = 5            # spacing between waveguides ( keep > 2 microns to minimize cross coupling)
  route_up = 250        # y-space (from top GC) for upward routing, increase if length of the contraDC is too exceeding the length of routes
  route_down = -153-wg_bend_radius   # y-space (from bottom GC) for downward routing, do not change this one

  
  

    
# TOP Function: Instatiate the layout functions
def contraDC_array():

  # Configure parameter sweep  polarization (unused so far)
  pol = 'te'
  
  # grab layout parameters
  params = parameters()
    
  print('Number of parameters to sweep: '+str(params.Num_sweep))

  # Import functions from SiEPIC-Tools, and get technology details
  from SiEPIC.utils import select_paths, get_layout_variables
  TECHNOLOGY, lv, ly, cell = get_layout_variables()
  dbu = ly.dbu
  from SiEPIC.extend import to_itype
  
  # clean all cells within the present cell
  ly.prune_subcells(cell.cell_index(), 100)
  
  # Layer mapping:
  LayerSiN = ly.layer(TECHNOLOGY['Si'])
  fpLayerN = cell.layout().layer(TECHNOLOGY['FloorPlan'])
  TextLayerN = cell.layout().layer(TECHNOLOGY['Text'])
  
  # Create a sub-cell for our contraDC layout
  top_cell = cell
  cell = cell.layout().create_cell("contraDC_GCarray")

  t = Trans(Trans.R0, 0, 0)
    
  # place the cell in the top cell
  top_cell.insert(CellInstArray(cell.cell_index(), t))
  
  # Grating couplers, Ports 1, 2, 3, 4 (top-down):
  GC_imported = ly.create_cell("ebeam_gc_%s1550" % pol, "EBeam").cell_index()
  gc_length = 41
  GC_pitch = 127
  
  # Instatiate GC array sufficient enough for the number of devices to be swept
  x = params.x_offset
  t = Trans(Trans.R0, 0, 0)
  cell.insert(CellInstArray(GC_imported, t, DPoint(0,GC_pitch/2).to_itype(dbu), DPoint(params.x_offset,0).to_itype(dbu), 8, params.Num_sweep/2))
   
  create_deviceArray()
  

# Instatiate the array of devices to sweep with their respective GC-device waveguide routes
def create_deviceArray():
  from SiEPIC.utils import select_paths, get_layout_variables
  from SiEPIC.scripts import path_to_waveguide
  from SiEPIC.extend import to_itype
  TECHNOLOGY, lv, ly, cell = get_layout_variables()
  LayerSiN = ly.layer(TECHNOLOGY['Si'])
  TextLayerN = cell.layout().layer(TECHNOLOGY['Text'])
  
  params = parameters()

   # Instatiate the devices array
  # Loop through the parameter sweep
  for i in range(params.Num_sweep):
      create_contraDC(x_pos = params.device_spacing*i + params.x_offset*params.Num_sweep/2, y_pos = 0, N = int(params.N[i]), 
      period = params.period[i], g = params.g[i], w1 = params.w1[i], w2 = params.w2[i], dW1 = params.dW1[i], dW2 = params.dW2[i], sine = params.sine, 
      a = params.a[i], sbend_L = params.sbend_L, sbend_R = params.sbend_R, sbend_H = params.sbend_H, taper_L = params.taper_L, wg_width = params.wg_width)
      
      # Interleaved compact routing
      
      # Regular routing points if device ID (i) is even
      if i % 2 == 0:
        initial_x = params.x_offset*(params.Num_sweep-2-i)/2
        device_x1 = params.x_offset + (i)*(params.x_offset/2 +params.device_spacing)+params.sbend_H      
        device_x2 = params.x_offset + (i)*(params.x_offset/2 +params.device_spacing)-params.w1[i]/2-params.g[i]-params.w2[i]/2
        device_y = -params.taper_L-params.sbend_L
        
        device_y_top = params.N[i]*params.period[i]+params.period[i]/2+params.sbend_L+params.taper_L
  
       # GC4 to device - downward routing
        route_y4 = params.route_down+params.GC_pitch-params.wg_pitch*i*2-params.wg_pitch
        dpath = DPath([DPoint(0,0), DPoint(params.wg_bend_radius,0), DPoint(params.wg_bend_radius,route_y4),
                                 DPoint(device_x1,route_y4),DPoint(device_x1,device_y)], params.wg_width).transformed(DTrans(DTrans.R0,initial_x, 0))
        cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
         
        # GC3 to device - downward routing
        route_y3 = params.route_down-params.wg_pitch*i*2
        dpath = DPath([DPoint(0,0), DPoint(params.wg_pitch + params.wg_bend_radius,0), DPoint(params.wg_pitch+params.wg_bend_radius, route_y3),
                                 DPoint(device_x2,route_y3),DPoint(device_x2,device_y-params.GC_pitch)], params.wg_width).transformed(DTrans(DTrans.R0,initial_x, params.GC_pitch))
        cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        # GC2 to device - upward routing (measurement label here!)
        route_y2 = params.route_up+params.wg_pitch*i*2
        dpath = DPath([DPoint(0,0), DPoint(params.wg_pitch + params.wg_bend_radius*2,0), DPoint(params.wg_pitch+params.wg_bend_radius*2, route_y2),
                                 DPoint(device_x2,route_y2),DPoint(device_x2,device_y_top-params.GC_pitch*2)], params.wg_width).transformed(DTrans(DTrans.R0,initial_x, params.GC_pitch*2))
        cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
        t = Trans(Trans.R0, to_itype(initial_x,dbu),to_itype(params.GC_pitch*2,dbu) )
        text = Text ("opt_in_TE_1550_device_ARcontraDC%dN%dperiod%dg%dwa%dwb%ddwa%ddwb%dsine%da" % (params.N[i],1000*params.period[i],1000*params.g[i],1000*params.w1[i],1000*params.w2[i],1000*params.dW1[i],1000*params.dW2[i],params.sine,10*params.a[i]),t)
        #text = Text ("opt_in_TE_1550_device_contraDC%f" % (int(params.N)),t)
        shape = cell.shapes(TextLayerN).insert(text)
        shape.text_size = 1.5/dbu
      
        # GC1 to device - upward routing
        route_y4 = params.route_up-params.GC_pitch+params.wg_pitch*i*2+params.wg_pitch
        dpath = DPath([DPoint(0,0), DPoint(params.wg_bend_radius*2,0), DPoint(params.wg_bend_radius*2,route_y4),
                                 DPoint(device_x1,route_y4),DPoint(device_x1,device_y_top-params.GC_pitch*3)], params.wg_width).transformed(DTrans(DTrans.R0,initial_x, params.GC_pitch*3))
        cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
      
    
    # Backwards routing points if device ID (i) is odd
      else:
        initial_x = params.x_offset*(params.Num_sweep-2-i)/2
        GC_x = params.x_offset/2
        device_x1 = params.x_offset + (i)*(params.x_offset/2 +params.device_spacing)+params.sbend_H
        device_x2 = params.x_offset + (i)*(params.x_offset/2 +params.device_spacing)-params.w1[i]/2-params.g[i]-params.w2[i]/2
        device_y = -params.taper_L-params.sbend_L
  
        device_y_top = params.N[i]*params.period[i]+params.period[i]/2+params.sbend_L+params.taper_L
  
        # GC4 to device - downward routing
        route_y4 = params.route_down+params.GC_pitch/2-params.wg_pitch*i*2
        dpath = DPath([DPoint(GC_x,0), DPoint(GC_x+params.wg_bend_radius,0),DPoint(GC_x+params.wg_bend_radius,-params.GC_pitch/4),DPoint(GC_x-params.x_offset/2,-params.GC_pitch/4), DPoint(GC_x-params.x_offset/2,route_y4),
                                 DPoint(device_x2,route_y4),DPoint(device_x2,device_y-params.GC_pitch/2)], params.wg_width).transformed(DTrans(DTrans.R0,initial_x, params.GC_pitch/2))
        cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        # GC3 to device - downward routing
        route_y3 = params.route_down+params.GC_pitch/2-params.wg_pitch*i*2-params.wg_pitch-params.GC_pitch
        dpath = DPath([DPoint(GC_x,0), DPoint(GC_x+params.wg_bend_radius,0),DPoint(GC_x+params.wg_bend_radius,-params.GC_pitch/4),DPoint(GC_x-params.x_offset/2-params.wg_pitch,-params.GC_pitch/4), DPoint(GC_x-params.x_offset/2-params.wg_pitch,route_y3),
                                 DPoint(device_x1,route_y3),DPoint(device_x1,device_y-params.GC_pitch/2-params.GC_pitch)], params.wg_width).transformed(DTrans(DTrans.R0,initial_x, 3*params.GC_pitch/2))
        cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        # GC2 to device - upward routing (measurement label here!)
        route_y2 = params.route_up+params.wg_pitch*i*2-params.GC_pitch/2+params.wg_pitch
        dpath = DPath([DPoint(GC_x,0), DPoint(GC_x+params.wg_bend_radius,0),DPoint(GC_x+params.wg_bend_radius,-params.GC_pitch/4),DPoint(GC_x-params.x_offset/2-params.wg_pitch,-params.GC_pitch/4), DPoint(GC_x-params.x_offset/2-params.wg_pitch,route_y2),
                                 DPoint(device_x1,route_y2),DPoint(device_x1,device_y_top-5*params.GC_pitch/2)], params.wg_width).transformed(DTrans(DTrans.R0,initial_x, 5*params.GC_pitch/2))
        cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
        
        # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
        t = Trans(Trans.R0, to_itype(initial_x+GC_x,dbu),to_itype(5*params.GC_pitch/2,dbu) )
        text = Text ("opt_in_TE_1550_device_contraDC%dN%dperiod%dg%dwa%dwb%ddwa%ddwb%dsine%da" % (params.N[i],1000*params.period[i],1000*params.g[i],1000*params.w1[i],1000*params.w2[i],1000*params.dW1[i],1000*params.dW2[i],params.sine,10*params.a[i]),t)
        #text = Text ("opt_in_TE_1550_device_contraDC%f" % (int(params.N)),t)
        shape = cell.shapes(TextLayerN).insert(text)
        shape.text_size = 1.5/dbu
        
        # GC1 to device
        route_y1 = params.route_up+params.wg_pitch*i*2-params.GC_pitch/2+params.wg_pitch-params.GC_pitch-params.wg_pitch
        dpath = DPath([DPoint(GC_x,0), DPoint(GC_x+params.wg_bend_radius,0),DPoint(GC_x+params.wg_bend_radius,-params.GC_pitch/4),DPoint(GC_x-params.x_offset/2,-params.GC_pitch/4), DPoint(GC_x-params.x_offset/2,route_y1),
                                 DPoint(device_x2,route_y1),DPoint(device_x2,device_y_top-7*params.GC_pitch/2)], params.wg_width).transformed(DTrans(DTrans.R0,initial_x, 7*params.GC_pitch/2))
        cell.shapes(LayerSiN).insert(dpath.to_itype(dbu))
      

  # Convert the paths to waveguides (very time consuming!)
  #path_to_waveguide(cell = cell, verbose=True, params = {'width': params.wg_width, 'adiabatic': params.bezier, 'radius': params.wg_bend_radius, 'bezier': params.bezier_N, 'wgs': [{'width': params.wg_width, 'layer': 'Si', 'offset': 0.0}]})
  
# Instatiate a complete contraDC PCell with s-bends, tapers, and waveguide routes
def create_contraDC(x_pos = 0, y_pos = 0, N = 1000, period = .318, g = .15, w1 = .56, w2 = .44, dW1 = .048, dW2 = .024, sine = 0, a = 2.7, sbend_L = 10, sbend_R = 13, sbend_H = 2, taper_L = 10, wg_width = 0.5):
  from SiEPIC.extend import to_itype
  from SiEPIC.utils import select_paths, get_layout_variables
  TECHNOLOGY, lv, ly, cell = get_layout_variables()
  
  # contraDC PCell
  pcell = ly.create_cell("Contra-Directional Coupler", "EBeam-dev", { "number_of_periods": N, "grating_period": period, "gap": g, "wg1_width": w1, "wg2_width": w2, "corrugation_width1": dW1, "corrugation_width2": dW2 , "sinusoidal": sine, "index": a} )
  t = Trans(Trans.R90, x_pos/dbu, to_itype(y_pos,dbu))
  cell.insert(CellInstArray(pcell.cell_index(),t))

  # S-Bend PCells (top and bottom)
  pcell = ly.create_cell("Waveguide_SBend", "EBeam", { "length": sbend_L, "height": sbend_H, "wg_width": w1, "radius": sbend_R} )
  t = Trans(Trans.R90, (x_pos+sbend_H)/dbu, to_itype(y_pos-sbend_L,dbu))
  cell.insert(CellInstArray(pcell.cell_index(),t))
  t = Trans(Trans.R270.M45, (x_pos)/dbu, to_itype(y_pos+N*period+period/2,dbu))
  cell.insert(CellInstArray(pcell.cell_index(),t))
  
  # Waveguide straight PCells (top and bottom
  pcell = ly.create_cell("Waveguide_Straight", "EBeam", { "wg_length": sbend_L/dbu, "wg_width": w2/dbu} )
  t = Trans(Trans.R90, (x_pos-w1/2-g-w2/2)/dbu, to_itype(y_pos-sbend_L/2,dbu))
  cell.insert(CellInstArray(pcell.cell_index(),t))
  t = Trans(Trans.R270.M45, (x_pos-w1/2-g-w2/2)/dbu, to_itype(y_pos+N*period+period/2+sbend_L/2,dbu))
  cell.insert(CellInstArray(pcell.cell_index(),t))
  
  # Waveguide taper PCells (top and bottom, left)
  pcell = ly.create_cell("ebeam_taper_te1550", "EBeam", { "wg_length": taper_L, "wg_width1": wg_width, "wg_width2": w2} )
  t = Trans(Trans.R90, (x_pos-w1/2-g-w2/2)/dbu, to_itype(y_pos-2*sbend_L,dbu))
  cell.insert(CellInstArray(pcell.cell_index(),t))
  t = Trans(Trans.R270, (x_pos-w1/2-g-w2/2)/dbu, to_itype(y_pos+N*period+period/2+2*sbend_L,dbu))
  cell.insert(CellInstArray(pcell.cell_index(),t))

  # Waveguide taper PCells (top and bottom, right)
  pcell = ly.create_cell("ebeam_taper_te1550", "EBeam", { "wg_length": taper_L, "wg_width1": wg_width, "wg_width2": w1} )
  t = Trans(Trans.R90, (x_pos+sbend_H)/dbu, to_itype(y_pos-2*sbend_L,dbu))
  cell.insert(CellInstArray(pcell.cell_index(),t))
  t = Trans(Trans.R270, (x_pos+sbend_H)/dbu, to_itype(y_pos+N*period+period/2+2*sbend_L,dbu))
  cell.insert(CellInstArray(pcell.cell_index(),t))

  
contraDC_array()

# All done!