#!python
# append meshes and textures into a single scene
# texture can be a image, a ireg file or a #RGB color code
# translate to origin: use to avoid errors when using data with UTM coordinates
# v1.0 01/2022 paulo.ernesto
'''
usage: $0 input_meshes#mesh*obj,msh,vtk,vtp,vtm,glb#texture*png,jpg,tiff,ireg translate_to_origin@ output*obj,msh,vtk,vtp,vtm,glb display@
'''
'''
Copyright 2022 Vale

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

*** You can contribute to the main repository at: ***

github.com/pemn/vtk_append
'''

import sys, os.path
import pandas as pd
import numpy as np

# import modules from a pyz (zip) file with same name as scripts
sys.path.insert(0, os.path.splitext(sys.argv[0])[0] + '.pyz')

from _gui import usage_gui, commalist, log
from pd_vtk import pv_read, pv_save, vtk_plot_meshes, vtk_path_to_texture, vtk_grid_to_mesh, vtk_ireg_to_texture, vtk_rgb_to_texture

def vtk_local_origin(meshes):
  bounds0 = None
  bounds1 = None
  for mesh in meshes:
    if bounds0 is None:
      bounds0 = bounds1 = mesh.bounds
    else:
      bounds0 = np.min([bounds0, mesh.bounds], 0)
      bounds1 = np.max([bounds1, mesh.bounds], 0)
  #bb = np.subtract(bounds1[1::2], bounds0[0::2])
  bb = np.subtract(bounds0[0::2], bounds1[1::2])
  tm = np.eye(4)
  tm[0:3, 3] = bb
  print(tm)
  for mesh in meshes:
    mesh.transform(tm, inplace=True)
  return meshes

def vtk_append(input_meshes, translate_to_origin = False, output = None, display = None):
  meshes = []
  for fp_m, fp_t in commalist().parse(input_meshes):
    log(fp_m)
    mesh = pv_read(fp_m)
    if isinstance(mesh, list):
      meshes.extend(mesh)
    elif mesh.GetDataObjectType() in [2,6]:
      meshes.extend(vtk_grid_to_mesh(mesh, fp_t))
    else:
      if fp_t.lower().endswith('ireg'):
        mesh = vtk_ireg_to_texture(mesh, fp_t)
      elif fp_t:
        if mesh.active_t_coords is None:
          mesh.texture_map_to_plane(inplace=True)
        if fp_t[0] == '#':
          mesh.textures[0] = vtk_rgb_to_texture(fp_t)
        elif os.path.exists(fp_t):
          mesh.textures[0] = vtk_path_to_texture(fp_t)
      meshes.append(mesh)

  if int(translate_to_origin):
    meshes = vtk_local_origin(meshes)

  if output:
    pv_save(meshes, output)

  if int(display):
    vtk_plot_meshes(meshes)

  log("# finished")

main = vtk_append

if __name__=="__main__":
  usage_gui(__doc__)
