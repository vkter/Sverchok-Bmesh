import bpy,bmesh,mathutils
from bpy.props import EnumProperty, FloatProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import (updateNode, enum_item as e, second_as_first_cycle as safc,match_long_repeat)

dict_mathutils = {"poly_3d_calc()": ["Calculate barycentric weights for a point on a polygon.", ["veclist","pt"], ['veclist – list of vectors','pt – point :rtype: list of per-vector weights'], "None"]}
types = []
for i,type in enumerate(dict_mathutils.keys()):
    types.append((type,type,dict_mathutils[type][0],i))

class SvMathuInterNode(SverchCustomTreeNode, bpy.types.Node):
    '''The Blender mathutils.interpolate module,Calculate barycentric weights for a point on a polygon.'''
    bl_idname = 'SvMathuInterNode'
    bl_label = 'Mathutils Interpolate'
    #bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_BM_MU'
    
    def updata_oper(self,context):
        for key in self.inputs.keys():
            self.safe_socket_remove('inputs',key)

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
            pars = match_long_repeat(pars)
            result = []
            for p in zip(*pars):
                for i in range(len(p)):
                    value = dict_mathutils[self.oper][1][i]
                    exec(value + '=p[i]')
                    if i == 0 :
                        param = value
                    else:
                        param += ','+value
                fun = 'mathutils.interpolate.' + self.oper[:-2] + '(' + param + ')'
                result.append(eval(fun))
            return_.append(result)
        return return_

def register():
    bpy.utils.register_class(SvMathuInterNode)


def unregister():
    bpy.utils.unregister_class(SvMathuInterNode)