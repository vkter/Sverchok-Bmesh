bl_info = {
    "name": "Sverchok-Bmesh",
    "author": "vkter",
    "version": (0, 1, 0, 0),
    "blender": (2, 81, 0),
    "location": "Node Editor",
    "category": "Node",
    "description": "Sverchok Bmesh",
    "warning": "",
    "wiki_url": "https://github.com/vkter/Sverchok-Bmesh/wiki",
    "tracker_url": "https://github.com/vkter/Sverchok-Bmesh/issues"
}

import sys
import importlib

import nodeitems_utils

from sverchok.utils.logging import info, debug
from sverchok.ui.nodeview_space_menu import add_node_menu

# make sverchok the root module name, (if sverchok dir not named exactly "sverchok")
if __name__ != "sverchok_bmesh":
    sys.modules["sverchok_bmesh"] = sys.modules[__name__]

from sverchok_bmesh import icons
from sverchok_bmesh import settings
from sverchok_bmesh import examples
from sverchok_bmesh.utils import show_welcome

def nodes_index():
    return [("Bmesh", [
                ('bmesh.bmesh_viewer','SvBMeshViewer'),
                ("bmesh.bmesh_in", "SvBMInNode"),
                ("bmesh.bmesh_out", "SvBMoutNode"),
                ("bmesh.bmesh_ops", "SvBMOpsNode"),
                ("bmesh.bmesh_ops_lite", "SvBMOpsLiteNode"),
                ("bmesh.bmesh_types", "SvBMTypesNode"),
                ("bmesh.bmesh_utils", "SvBMUtilsNode"),
                ("bmesh.bmesh_geometry", "SvBMGeometryNode"),
                ('bmesh.mathutils','SvMathutilsNode'),
                ('bmesh.mathutils_geometry','SvMathuGeoNode'),
                ('bmesh.mathutils_bvhtree','SvMathuBvhNode'),
                ('bmesh.mathutils_kdtree','SvMathuKdNode'),
                ('bmesh.mathutils_interpolate','SvMathuInterNode'),
                ('bmesh.mathutils_noise','SvMathuNoiseNode')
            ])
    ]


def convert_config(config):
    new_form = []
    for cat_name, items in config:
        new_items = []
        for item in items:
            if item is None:
                new_items.append('---')
                continue
            path, bl_idname = item
            new_items.append(bl_idname)
        cat = {cat_name: new_items}
        new_form.append(cat)
    return new_form


add_node_menu.append_from_config(convert_config(nodes_index()))


def make_node_list():
    modules = []
    base_name = "sverchok_bmesh.nodes"
    index = nodes_index()
    for category, items in index:
        for item in items:
            if not item:
                continue
            module_name, node_name = item
            module = importlib.import_module(f".{module_name}", base_name)
            modules.append(module)
    return modules

imported_modules = [icons] + make_node_list()

reload_event = False

if "bpy" in locals():
    reload_event = True
    info("Reloading sverchok-bmesh...")

import bpy

def register_nodes():
    node_modules = make_node_list()
    for module in node_modules:
        module.register()
    info("Registered %s nodes", len(node_modules))

def unregister_nodes():
    global imported_modules
    for module in reversed(imported_modules):
        module.unregister()


our_menu_classes = []

def reload_modules():
    global imported_modules
    for im in imported_modules:
        debug("Reloading: %s", im)
        importlib.reload(im)

def register():
    global our_menu_classes

    debug("Registering Sverchok-Bmesh")

    add_node_menu.register()
    settings.register()
    icons.register()

    register_nodes()

    examples.register()

    show_welcome()

def unregister():
    global our_menu_classes
    if 'SVERCHOK_BMESH' in nodeitems_utils._node_categories:
        nodeitems_utils.unregister_node_categories("SVERCHOK_BMESH")
    for clazz in our_menu_classes:
        try:
            bpy.utils.unregister_class(clazz)
        except Exception as e:
            print("Can't unregister menu class %s" % clazz)
            print(e)
    unregister_nodes()

    icons.unregister()
    settings.unregister()
