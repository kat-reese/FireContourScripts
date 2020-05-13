import numpy as np
import os
import sys
from pathlib import Path
import rasterio as rst
from rasterio.crs import CRS
from rasterio.enums import Resampling
from rasterio import shutil as rio_shutil
from rasterio.vrt import WarpedVRT

import rasterio.features
import rasterio.warp
import rasterio.transform
import affine
import matplotlib.pyplot as plt
import cv2 as cv


class ReduceImages:
    def __init__(self):
        if not os.path.exists("Reduced"):
            os.makedirs("Reduced")
        reduction_size = float(sys.argv[2])
        dst_crs = rst.crs.CRS.from_epsg(4326)
        for image_path in self.image_locations(sys.argv[1]):
            name = self.get_file_name(image_path)
            print(name)
            if not os.path.exists("Reduced/"+name):
                with rst.open(image_path) as src:
                    band = src.read(1)
                    meta = src.profile

                    top = 0 
                    left = 0 
                    bottom = band.shape[0]
                    right = band.shape[1]

                    print("top: ", top)
                    print("bottom: ", bottom)
                    print("left: ", left)
                    print("right: ", right)

                    dst_width = int((right - left) * reduction_size)
                    dst_height = int((bottom - top) * reduction_size)

                    print("previous width: ", band.shape[1])
                    print("dst_width: ", dst_width)
                    print("previous height: ", band.shape[0])
                    print("dst_height: ", dst_height)

                    leftCoord, topCoord = src.xy(top, left)
                    rightCoord, bottomCoord = src.xy(bottom, right)

                    xres = (rightCoord - leftCoord) / dst_width
                    yres = (topCoord - bottomCoord) / dst_height
                    dst_transform = affine.Affine(xres, 0.0, leftCoord, 0.0, -yres, topCoord)
                    vrt_options = {
                        'resampling': rst.enums.Resampling.cubic,
                        'crs':dst_crs,
                        'transform':dst_transform,
                        'height':dst_height,
                        'width':dst_width
                    }
                    with WarpedVRT(src, **vrt_options) as vrt:
                        rio_shutil.copy(vrt, "Reduced/"+name, driver='GTiff')


    ###################################################
    ##       Function: image_locations               ##
    ## Retrieves file paths from the designated      ##
    ## directory, and returns a numpy array of file  ##
    ## names.                                        ##
    ###################################################
    def image_locations(self, path="Original_Images"):
        dir = Path(path)
        image_names = []
        for file in dir.glob('*.tif'):
            file_name = os.path.dirname(file) + "/" + os.path.basename(file)
            image_names.append(file_name) 
            image_names.sort()       
        return np.asarray(image_names)

    ###################################################
    ##       Function: get_file_name                 ##
    ## Parses the file name from a path string.      ##
    ###################################################
    def get_file_name(self, image_path):
        index_slash = image_path.rfind('/')
        return image_path[index_slash+1:len(image_path)]


def main():
    reduction = ReduceImages()

if __name__ == '__main__':
    main()
