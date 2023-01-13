from itertools import cycle

import bpy
from bpy.props import BoolProperty

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, repeat_last
from sverchok.utils.nodes_mixins.generating_objects import SvMeshData, SvViewerNode
from sverchok.utils.handle_blender_data import correct_collection_length
from sverchok.utils.nodes_mixins.show_3d_properties import Show3DProperties
import sverchok.utils.meshes as me
from sverchok.utils.logging import fix_error_msg


class SvBMeshViewer(Show3DProperties, SvViewerNode, SverchCustomTreeNode, bpy.types.Node):
    """
    Triggers: viewer Bmesh object instance
    Tooltip: Generate/Update mesh objects in viewport. 
    """

    bl_idname = 'SvBMeshViewer'
    bl_label = 'BMesh Viewer'
    sv_icon = 'SV_BM_BM'

    show_wireframe: BoolProperty(default=True, update=updateNode, name="Show Edges")
    
    free : BoolProperty(
    name = "Free Bmesh",
    description="Destroy the bmesh object from memory",
    default = True,
    update = updateNode)

    def sv_init(self, context):
        self.init_viewer()
        self.inputs.new('SvStringsSocket', 'Bmesh').custom_draw = 'draw_edges_props'

    def draw_buttons(self, context, layout):
        self.draw_viewer_properties(layout)
        layout.prop(self,'free')

    def draw_edges_props(self, socket, context, layout):
        socket.draw_quick_link(context, layout, self)
        layout.label(text=socket.name)
        layout.prop(self, 'show_wireframe', text='', expand=True,
                    icon='HIDE_OFF' if self.show_wireframe else 'HIDE_ON')

    def draw_label(self):
        if self.hide:
            return f"MeV {self.base_data_name}"
        else:
            return "BMesh Viewer"

    def process(self):

        if not self.is_active:
            return

        Bmesh = self.inputs['Bmesh'].sv_get(default=[])

        #get name
        names = [self.base_data_name+str(i) for i in range(len(Bmesh))]

        # regenerate mesh data blocks
        meshes = []
        for name,bm in zip(names,Bmesh):
            ind = bpy.data.meshes.find(name)
            if ind != -1:
                mesh = bpy.data.meshes[ind]
            else:
                mesh = bpy.data.meshes.new(name=name)
            bm.to_mesh(mesh)
            meshes.append(mesh)
            if self.free:
                bm.free()
        
        # regenerate object data blocks
        self.regenerate_objects(names,
                                meshes,
                                [self.collection],
                                to_show=[self.id_data.sv_show and self.show_objects]
                                )
        [setattr(prop.obj, 'show_wire', self.show_wireframe) for prop in self.object_data]

        self.outputs['Objects'].sv_set([obj_data.obj for obj_data in self.object_data])


register, unregister = bpy.utils.register_classes_factory([SvBMeshViewer])
