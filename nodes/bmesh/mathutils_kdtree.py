import bpy,bmesh,mathutils
from bpy.props import EnumProperty, FloatProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import (updateNode, enum_item as e, second_as_first_cycle as safc,match_long_repeat)

dict_mathutils = {"KDTree()": ["new kd-tree initialized to hold items.size\nNote\nKDTree.balance must have been called before using any of the methods.find\n", ["size"], ['KdTree size'], "None"], "balance()": ["Balance the tree.\nNote\nThis builds the entire tree, avoid calling after each insertion.\n", [], [], "None"], "find()": ["Find nearest point to .co\n", ["co", "filter"], ["co (float triplet) \u2013 3d coordinates.\n", "filter (callable) \u2013 function which takes an index and returns True for indices to include in the search.\n"], "Returns\nReturns (, index, distance).Vector\nReturn type\ntuple\n"], "find_n()": ["Find nearest points to .nco\n", ["co", "n"], ["co (float triplet) \u2013 3d coordinates.\n", "n (int) \u2013 Number of points to find.\n"], "Returns\nReturns a list of tuples (, index, distance).Vector\nReturn type\nlist\n"], "find_range()": ["Find all points within of .radiusco\n", ["co", "radius"], ["co (float triplet) \u2013 3d coordinates.\n", "radius (float) \u2013 Distance to search for points.\n"], "Returns\nReturns a list of tuples (, index, distance).Vector\nReturn type\nlist\n"], "insert()": ["Insert a point into the KDTree.\n", ["co", "index"], ["co (float triplet) \u2013 Point 3d position.\n", "index (int) \u2013 The index of the point."], "None"]}
types = []
for i,type in enumerate(dict_mathutils.keys()):
    types.append((type,type,dict_mathutils[type][0],i))
class_fun = ["KDTree()"]

class SvMathuKdNode(SverchCustomTreeNode, bpy.types.Node):
    '''The Blender mathutils.kdtree module,Generic 3-dimensional kd-tree to perform spatial searches.'''
    bl_idname = 'SvMathuKdNode'
    bl_label = 'Mathutils Kdtree'
    #bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_BM_MU'
    
    def updata_oper(self,context):
        for key in self.inputs.keys():
            self.safe_socket_remove('inputs',key)

        if self.oper not in class_fun:
            self.inputs.new('SvStringsSocket','input').description = 'Input kdtree'
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
        description = 'Operator of mathutils.kdtree',
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
                fun = 'mathutils.kdtree.' + self.oper[:-2] + '(' + 'pars[0]' + ')' 
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
    bpy.utils.register_class(SvMathuKdNode)


def unregister():
    bpy.utils.unregister_class(SvMathuKdNode)