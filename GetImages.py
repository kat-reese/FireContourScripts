import numpy as np
import os
import sys
from pathlib import Path
class GetImages:
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