#Copyright (C) 2016 Daruma Labs
#info@daruma-labs.be
#
#Created by Joeri Gydé
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Blender Architect",
    "description": "Architectural objects for Blender",
    "author": "Joeri Gyde",
    "version": (0, 0, 1),
    "blender": (2, 75, 0),
    "location": "View3D",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Object" }


import bpy


# load and reload submodules
##################################

import importlib
import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.reload_addon_modules(__path__, __name__, "bpy" in locals())

# register
##################################

import traceback

def menu_func(self, context):
    self.layout.menu("view3d.architect_menu", icon="PLUGIN")

def register():
    try: 
        bpy.utils.register_module(__name__)
        bpy.types.INFO_MT_mesh_add.append(menu_func)
        developer_utils.setup_addon_modules(__name__,modules)
    except: traceback.print_exc()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    try: 
        developer_utils.teardown_addon_modules(__name__,modules)
        bpy.utils.unregister_module(__name__)
        bpy.types.INFO_MT_mesh_add.remove(menu_func) 
    except: traceback.print_exc()

    print("Unregistered {}".format(bl_info["name"]))
