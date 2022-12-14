"""
Copyright (C) 2014 John Evans

This example code illustrates how to access and visualize an LP DAAC MCD19A2
v6 HDF-EOS2 Sinusoidal Grid file in Python.

If you have any questions, suggestions, or comments on this example, please use
the HDF-EOS Forum (http://hdfeos.org/forums).  If you would like to see an
example of any other NASA HDF/HDF-EOS data product that is not listed in the
HDF-EOS Comprehensive Examples page (http://hdfeos.org/zoo), feel free to
contact us at eoshelp@hdfgroup.org or post it at the HDF-EOS Forum
(http://hdfeos.org/forums).

Usage:  save this script and run

    $python MCD19A2.A2010010.h25v06.006.2018047103710.hdf.py


Tested under: Python 3.7.3 :: Anaconda custom (64-bit)
Last updated: 2020-07-23
"""
import os
import re
import pyproj

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from pyhdf.SD import SD, SDC
# from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import matplotlib.patheffects as path_effects
import sys as s
import cartopy.feature as cfeature
import os 
import cartopy as cartopy
from cartopy import config
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

FILE_NAME = r'C:\Users\IITM\Desktop\MCD19A2.A2010010.h25v06.006.2018047103710.hdf'
DATAFIELD_NAME = 'Optical_Depth_055'
hdf = SD(FILE_NAME, SDC.READ)

# Read dataset.
data3D = hdf.select(DATAFIELD_NAME)
data = data3D[0,:,:].astype(np.double)

# Read attributes.
attrs = data3D.attributes(full=1)
lna=attrs["long_name"]
long_name = lna[0]
vra=attrs["valid_range"]
valid_range = vra[0]
fva=attrs["_FillValue"]
_FillValue = fva[0]
sfa=attrs["scale_factor"]
scale_factor = sfa[0]        
ua=attrs["unit"]
units = ua[0]
aoa=attrs["add_offset"]
add_offset = aoa[0]

# Apply the attributes to the data.
invalid = np.logical_or(data < valid_range[0], data > valid_range[1])
invalid = np.logical_or(invalid, data == _FillValue)
data[invalid] = np.nan
data = (data - add_offset) * scale_factor
data = np.ma.masked_array(data, np.isnan(data))

# Construct the grid.  The needed information is in a global attribute
# called 'StructMetadata.0'.  Use regular expressions to tease out the
# extents of the grid.
fattrs = hdf.attributes(full=1)
ga = fattrs["StructMetadata.0"]
gridmeta = ga[0]
ul_regex = re.compile(r'''UpperLeftPointMtrs=\(
                          (?P<upper_left_x>[+-]?\d+\.\d+)
                          ,
                          (?P<upper_left_y>[+-]?\d+\.\d+)
                          \)''', re.VERBOSE)

match = ul_regex.search(gridmeta)
x0 = np.float(match.group('upper_left_x'))
y0 = np.float(match.group('upper_left_y'))

lr_regex = re.compile(r'''LowerRightMtrs=\(
                          (?P<lower_right_x>[+-]?\d+\.\d+)
                          ,
                          (?P<lower_right_y>[+-]?\d+\.\d+)
                          \)''', re.VERBOSE)
match = lr_regex.search(gridmeta)
x1 = np.float(match.group('lower_right_x'))
y1 = np.float(match.group('lower_right_y'))
        
nx, ny = data.shape
x = np.linspace(x0, x1, nx, endpoint=False)
y = np.linspace(y0, y1, ny, endpoint=False)
xv, yv = np.meshgrid(x, y)

sinu = pyproj.Proj("+proj=sinu +R=6371007.181 +nadgrids=@null +wktext")
wgs84 = pyproj.Proj("+init=EPSG:4326") 
lon, lat= pyproj.transform(sinu, wgs84, xv, yv)

# m = Basemap(projection='cyl', resolution='l',
#             llcrnrlat=np.min(lat),  urcrnrlat=np.max(lat),
#             llcrnrlon=np.min(lon), urcrnrlon=np.max(lon))
# m.drawcoastlines(linewidth=0.5)
# m.drawparallels(np.arange(np.floor(np.min(lat)), np.ceil(np.max(lat)), 5),
#                 labels=[1, 0, 0, 0])
# m.drawmeridians(np.arange(np.floor(np.min(lon)), np.ceil(np.max(lon)), 5),
#                 labels=[0, 0, 0, 1])
# m.scatter(lon, lat, c=data, s=1, cmap=plt.cm.jet,
#           edgecolors=None, linewidth=0)

# cb = m.colorbar()
# cb.set_label(units)

# basename = os.path.basename(FILE_NAME)
# plt.title('{0}\n{1}'.format(basename, long_name))
# fig = plt.gcf()
# pngfile = "{0}.py.png".format(basename)
# fig.savefig(pngfile)


plt.figure(figsize=(15,12),facecolor = 'none')
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([np.min(lon),np.max(lon),np.min(lat),np.max(lon)], crs=ccrs.PlateCarree()) # [lonmin,lonmax,latmin,latmax]
ax.coastlines()
# ax.add_geometries(adm1_shapes, ccrs.PlateCarree(),
                  # edgecolor='black', alpha=0.5,lw = 2, facecolor='none') #
#     ax.add_feature(cfeature.LAND, edgecolor='black')
#     ax.add_feature(cfeature.BORDERS)
#     ax.add_feature(cfeature.STATES.with_scale('10m'),
#                linestyle='-', alpha=.25, facecolor='none', edgecolor='black')
    
ax.add_feature(cfeature.COASTLINE)
ax.gridlines()
filled_c = ax.pcolormesh(lon, lat, c=data,cmap = 'jet',vmin = 294 , vmax = 298,
                           transform=ccrs.PlateCarree())
gl = ax.gridlines(draw_labels=True)
gl.top_labels = False
gl.right_labels = False
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {'size': 12,'color': 'red', 'weight': 'bold'}
gl.ylabel_style = {'size': 12,'color': 'red', 'weight': 'bold'}
        # Add a colorbar for the filled contour.
plt.colorbar(filled_c,ax=ax, orientation='horizontal')
plt.title('Osmanabad')
plt.show()