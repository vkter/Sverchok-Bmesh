import bpy,bmesh,mathutils
from bpy.props import EnumProperty, FloatProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import (updateNode, enum_item as e, second_as_first_cycle as safc,match_long_repeat)

dict_mathutils = {"FromBMesh()": ["BVH tree based on BMesh data.\n", ["bmesh", "epsilon"], ["bmesh (BMesh) \u2013 BMesh data.\n", "epsilon (float) \u2013 Increase the threshold for detecting overlap and raycast hits.\n"], "None"], "FromObject()": ["BVH tree based on Object data.\n", ["object", "depsgraph", "deform", "render", "cage", "epsilon"], ["object (Object) \u2013 Object data.\n", "depsgraph (Depsgraph) \u2013 Depsgraph to use for evaluating the mesh.\n", "deform (bool) \u2013 Use mesh with deformations.\n", "None", "cage (bool) \u2013 Use modifiers cage.\n", "epsilon (float) \u2013 Increase the threshold for detecting overlap and raycast hits.\n"], "None"], "FromPolygons()": ["BVH tree constructed geometry passed in as arguments.\n", ["vertices", "polygons", "all_triangles", "epsilon"], ["vertices (float triplet sequence) \u2013 float triplets each representing (x, y, z)\n", "polygons (Sequence of sequences containing ints) \u2013 Sequence of polyugons, each containing indices to the vertices argument.\n", "all_triangles (bool) \u2013 Use when all polygons are triangles for more efficient conversion.\n", "epsilon (float) \u2013 Increase the threshold for detecting overlap and raycast hits.\n"], "None"], "find_nearest()": ["Find the nearest element (typically face index) to a point.\n", ["origin", "distance"], [" (Vector) – Find nearest element to this point.", "distance (float) \u2013 Maximum distance threshold.\n"], "Returns\nReturns a tuple (Vector location, Vector normal, int index, float distance), Values will all be None if no hit is found.\nReturn type\ntuple\n"], "find_nearest_range()": ["Find the nearest elements (typically face index) to a point in the distance range.\n", ["origin", "distance"], [" (Vector) – Find nearest element to this point.", "distance (float) \u2013 Maximum distance threshold.\n"], "Returns\nReturns a list of tuples (Vector location, Vector normal, int index, float distance),\nReturn type\nlist\n"], "overlap()": ["Find overlapping indices between 2 trees.\n", ["other_tree"], ["other_tree (BVHTree) \u2013 Other tree to perform overlap test on.\n"], "Returns\nReturns a list of unique index pairs, the first index referencing this tree, the second referencing the other_tree.\nReturn type\nlist\n"], "ray_cast()": ["Cast a ray onto the mesh.\n", ["origin", "direction", "distance"], ["origin (Vector) \u2013 Start location of the ray in object space.\n", "direction (Vector) \u2013 Direction of the ray in object space.\n", "distance (float) \u2013 Maximum distance threshold.\n"], "Returns\nReturns a tuple (Vector location, Vector normal, int index, float distance), Values will all be None if no hit is found.\nReturn type\ntuple"]}
types = []
for i,type in enumerate(dict_mathutils.keys()):
    types.append((type,type,dict_mathutils[type][0],i))
class_fun = ['FromBMesh()', 'FromObject()', 'FromPolygons()']

class SvMathuBvhNode(SverchCustomTreeNode, bpy.types.Node):
    '''The Blender mathutils.bvhtree module,BVH tree structures for proximity searches and ray casts on geometry.'''
    bl_idname = 'SvMathuBvhNode'
    bl_label = 'Mathutils Bvhtree'
    #bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_BM_MU'
    
    def updata_oper(self,context):
        for key in self.inputs.keys():
            self.safe_socket_remove('inputs',key)

        if self.oper not in class_fun:
            self.inputs.new('SvStringsSocket','input').description = 'Input bvhtree data'
        for i,p in enumerate(dict_mathutils[self.oper][1]):
            pras = dict_mathutils[self.oper][2]
            if pras:
                des = pras[i]
            else:
                des = 'None'
            self.inputs.new('SvStringsSocket',p).description = des
        self.outputs['return'].description = dict_mathutils[self.oper][-1]
        updateNode(self,context)

    oper: EnumProperty(
        name='Operators',
        description = 'Operator of mathutils.bvhtree',
        items= types,
        update=updata_oper)
    
    def draw_buttons(self, context, layout):
        layout.prop(self,'oper',text='')

    def sv_init(self, context):
        for i,p in enumerate(dict_mathutils[self.oper][1]):
            des = dict_mathutils[self.oper][2][i]
            self.inputs.new('SvStringsSocket',p).description = des
        self.outputs.new('SvStringsSocket','return').description = dict_mathutils[self.oper][-1]
        
    def process(self):
        input = []
        for p in self.inputs.keys():
            value = self.inputs[p].sv_get(default = [])
            input.append(value)
        input = match_long_repeat(input)

        if self.inputs[0].is_linked:
            return_ = self.proce(input)
        else:
            return_ = []
        self.outputs['return'].sv_set(return_)

    def proce(self,input):
        return_ = []
        for pars in zip(*input):
            if self.oper in class_fun:
                for i in range(len(pars)):
                    name_p = dict_mathutils[self.oper][1][i]
                    value = name_p
                    exec(value + '=pars[i]')
                    if i == 0 :
                        param = name_p + '=' + value
                    else:
                        param += ','+ name_p + '=' + value
                fun = 'mathutils.bvhtree.BVHTree.' + self.oper[:-2] + '(' + param + ')' 
                return_.append(eval(fun))
            else:
                pars = match_long_repeat(pars)
                result = []
                for p in zip(*pars):
                    for i in range(len(p)-1):
                        value = dict_mathutils[self.oper][1][i]
                        exec(value + '=p[i+1]')
                        if i == 0 :
                            param = value
                        else:
                            param += ','+value
                    fun = 'p[0].' + self.oper[:-2] + '(' + param + ')'
                    result.append(eval(fun))
                return_.append(result)
        return return_

def register():
    bpy.utils.register_class(SvMathuBvhNode)


def unregister():
    bpy.utils.unregister_class(SvMathuBvhNode)