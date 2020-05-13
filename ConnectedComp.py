import numpy as np
import os
import sys
import gc
from pathlib import Path
import rasterio as rst
import matplotlib.pyplot as plt
import cv2 as cv
from scipy.ndimage import gaussian_filter
from GetImages import GetImages
# from skimage import measure
# from scipy.stats import itemfreq
# import matplotlib.animation as animation
# from MP4Maker import MP4Maker
import cc3d

class ConnectedComp:
   image_retrieval = GetImages()
   ###################################################
   ##       Function: image_locations               ##
   ## Retrieves file paths from the designated      ##
   ## directory, and returns a numpy array of file  ##
   ## names.                                        ##
   ###################################################
   def image_locations(self, path="Original_Images"):
      dir = Path(path)
      image_names = []
      for file in dir.glob('*.tif*'):
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

   ###################################################
   ##       Function: apply_connected_comp          ##
   ## Applies connected components to the images    ##
   ## in order to track parts of the fire over time.##
   ###################################################
   def apply_connected_comp(self, apply_directory, save_directory, num_components=100, num_images = 960):
      index_slash = save_directory.rfind('/')
      directory = save_directory[0:index_slash]
      print("Applying Connected Components...")
      if not os.path.exists(directory):
         os.makedirs(directory)    
      file_names = []
      images = []
      meta = []
      meta.append(['driver', 'dtype', 'nodata', 'width', 'height', 'count', 'crs', 'pixel width', 'row rotation', 'upperleftx_coord', 'column rotation', 'pixel height','upperlefty_coord', 'blockxsize', 'blockysize', 'tiled', 'compress', 'interleave'])
      index = 0
      save_iter = 1
      prev_iter = 0
      num_iter = num_images
      image_array = self.image_retrieval.image_locations(apply_directory)
      for image_path in image_array:
         if index == num_iter:   
            print("prev_iter=", prev_iter)
            print('save_iter=', save_iter)
            print('num_iter=', num_iter)
            file_names = np.asarray(file_names)
            images = np.asarray(images)
            meta = np.asarray(meta)
            connectivity = 6 
            print("Connecting Components...")
            labeled_data = cc3d.connected_components(images, connectivity=connectivity)
            labeled_data[labeled_data > int(num_components)] = 0

            print("Saving Images",prev_iter,"-",(num_iter - 1),"...")
            np.save(save_directory + str(prev_iter) + "_" + str(num_iter - 1) + ".npy", labeled_data)
            print("Saving Names",prev_iter,"-",(num_iter - 1),"...")
            np.save(save_directory + str(prev_iter) + "_" + str(num_iter - 1) + "_names.npy", file_names)
            print("Saving Meta",prev_iter,"-",(num_iter - 1),"...")
            np.save(save_directory + str(prev_iter) + "_" + str(num_iter - 1) + "_meta.npy", meta)

            prev_iter = num_iter
            save_iter += 1
            num_iter *= save_iter
            print("prev_iter=", prev_iter)
            print('save_iter=', save_iter)
            print('num_iter=', num_iter)
            file_names = []
            meta = []
            images = []
            labeled_data = []
            gc.collect()

         name = self.image_retrieval.get_file_name(image_path)
         raster = rst.open(image_path)
         profile = raster.profile
         image = raster.read(1)
         image[image == 255] = 1
         file_names.append(name)
         images.append(image)
         pixel_transform = profile['transform']
         meta.append(['GTiff', 'uint8', 0.0, 2462, 3500, 1, 'epsg:4326', pixel_transform[0], pixel_transform[1], pixel_transform[2], pixel_transform[3], pixel_transform[4], pixel_transform[5], 256, 256, True, 'deflate', 'band'])
         index += 1
         raster.close()

def main():
   print("Notice: Please note that this script is intended to run after KMeansConverter.py. If it is executed after a different script it will not work.")
   cc = ConnectedComp()
   if len(sys.argv) < 2:
      print("Please enter the directory of the images you would like to compress and the new directory for the compressed images.")
   elif sys.argv[1].lower() == "cc" and len(sys.argv) == 5:
      cc.apply_connected_comp(sys.argv[2], sys.argv[3], sys.argv[4])
   elif sys.argv[1].lower() == "cc" and len(sys.argv) != 5:
      print("To apply connected components to images please enter: cc image_directory_to_apply save_directory number_components")
   else:
      print("To apply connected components to images please enter: cc image_directory_to_apply save_directory number_components")

if __name__ == "__main__":
   main()