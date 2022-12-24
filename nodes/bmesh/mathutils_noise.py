import bpy,bmesh,mathutils
from bpy.props import EnumProperty, FloatProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import (updateNode, enum_item as e, second_as_first_cycle as safc,match_long_repeat)

dict_mathutils = {"cell()": ["Returns cell noise value at the specified position.\n", ["position"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n"], "Returns\nThe cell noise value.\nReturn type\nfloat\n"], "cell_vector()": ["Returns cell noise vector at the specified position.\n", ["position"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n"], "Returns\nThe cell noise vector.\nReturn type\nmathutils.Vector\n"], "fractal()": ["Returns the fractal Brownian motion (fBm) noise value from the noise basis at the specified position.\n", ["position", "H", "lacunarity", "octaves", "noise_basis"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "H (float) \u2013 The fractal increment factor.\n", "lacunarity (float) \u2013 The gap between successive frequencies.\n", "octaves (int) \u2013 The number of different noise frequencies used.\n", "noise_basis (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n"], "Returns\nThe fractal Brownian motion noise value.\nReturn type\nfloat\n"], "hetero_terrain()": ["Returns the heterogeneous terrain value from the noise basis at the specified position.\n", ["position", "H", "lacunarity", "octaves", "offset", "noise_basis"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "H (float) \u2013 The fractal dimension of the roughest areas.\n", "lacunarity (float) \u2013 The gap between successive frequencies.\n", "octaves (int) \u2013 The number of different noise frequencies used.\n", "offset (float) \u2013 The height of the terrain above \u2018sea level\u2019.\n", "noise_basis (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n"], "Returns\nThe heterogeneous terrain value.\nReturn type\nfloat\n"], "hybrid_multi_fractal()": ["Returns hybrid multifractal value from the noise basis at the specified position.\n", ["position", "H", "lacunarity", "octaves", "offset", "gain", "noise_basis"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "H (float) \u2013 The fractal dimension of the roughest areas.\n", "lacunarity (float) \u2013 The gap between successive frequencies.\n", "octaves (int) \u2013 The number of different noise frequencies used.\n", "offset (float) \u2013 The height of the terrain above \u2018sea level\u2019.\n", "gain (float) \u2013 Scaling applied to the values.\n", "noise_basis (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n"], "Returns\nThe hybrid multifractal value.\nReturn type\nfloat\n"], "multi_fractal()": ["Returns multifractal noise value from the noise basis at the specified position.\n", ["position", "H", "lacunarity", "octaves", "noise_basis"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "H (float) \u2013 The fractal increment factor.\n", "lacunarity (float) \u2013 The gap between successive frequencies.\n", "octaves (int) \u2013 The number of different noise frequencies used.\n", "noise_basis (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n"], "Returns\nThe multifractal noise value.\nReturn type\nfloat\n"], "noise()": ["Returns noise value from the noise basis at the position specified.\n", ["position", "noise_basis"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "noise_basis (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n"], "Returns\nThe noise value.\nReturn type\nfloat\n"], "noise_vector()": ["Returns the noise vector from the noise basis at the specified position.\n", ["position", "noise_basis"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "noise_basis (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n"], "Returns\nThe noise vector.\nReturn type\nmathutils.Vector\n"], "random()": ["Returns a random number in the range [0, 1).\n", [], [], "Returns\nThe random number.\nReturn type\nfloat\n"], "random_unit_vector()": ["Returns a unit vector with random entries.\n", ["size"], ["size (int) \u2013 The size of the vector to be produced, in the range [2, 4].\n"], "Returns\nThe random unit vector.\nReturn type\nmathutils.Vector\n"], "random_vector()": ["Returns a vector with random entries in the range (-1, 1).\n", ["size"], ["size (int) \u2013 The size of the vector to be produced.\n"], "Returns\nThe random vector.\nReturn type\nmathutils.Vector\n"], "ridged_multi_fractal()": ["Returns ridged multifractal value from the noise basis at the specified position.\n", ["position", "H", "lacunarity", "octaves", "offset", "gain", "noise_basis"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "H (float) \u2013 The fractal dimension of the roughest areas.\n", "lacunarity (float) \u2013 The gap between successive frequencies.\n", "octaves (int) \u2013 The number of different noise frequencies used.\n", "offset (float) \u2013 The height of the terrain above \u2018sea level\u2019.\n", "gain (float) \u2013 Scaling applied to the values.\n", "noise_basis (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n"], "Returns\nThe ridged multifractal value.\nReturn type\nfloat\n"], "seed_set()": ["Sets the random seed used for random_unit_vector, and random.\n", ["seed"], ["seed (int) \u2013 Seed used for the random generator. When seed is zero, the current time will be used instead.\n"], "None"], "turbulence()": ["Returns the turbulence value from the noise basis at the specified position.\n", ["position", "octaves", "hard", "noise_basis", "amplitude_scale", "frequency_scale"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "octaves (int) \u2013 The number of different noise frequencies used.\n", "hard (boolean) \u2013 Specifies whether returned turbulence is hard (sharp transitions) or soft (smooth transitions).\n", "noise_basis (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n", "amplitude_scale (float) \u2013 The amplitude scaling factor.\n", "frequency_scale (float) \u2013 The frequency scaling factor\n"], "Returns\nThe turbulence value.\nReturn type\nfloat\n"], "turbulence_vector()": ["Returns the turbulence vector from the noise basis at the specified position.\n", ["position", "octaves", "hard", "noise_basis", "amplitude_scale", "frequency_scale"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "octaves (int) \u2013 The number of different noise frequencies used.\n", "hard (boolean) \u2013 Specifies whether returned turbulence is hard (sharp transitions) or soft (smooth transitions).\n", "noise_basis (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n", "amplitude_scale (float) \u2013 The amplitude scaling factor.\n", "frequency_scale (float) \u2013 The frequency scaling factor\n"], "Returns\nThe turbulence vector.\nReturn type\nmathutils.Vector\n"], "variable_lacunarity()": ["Returns variable lacunarity noise value, a distorted variety of noise, from noise type 1 distorted by noise type 2 at the specified position.\n", ["position", "distortion", "noise_type1", "noise_type2"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "distortion (float) \u2013 The amount of distortion.\n", "noise_type1 (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n", "noise_type2 (string) \u2013 Enumerator in [\u2018BLENDER\u2019, \u2018PERLIN_ORIGINAL\u2019, \u2018PERLIN_NEW\u2019, \u2018VORONOI_F1\u2019, \u2018VORONOI_F2\u2019, \u2018VORONOI_F3\u2019, \u2018VORONOI_F4\u2019, \u2018VORONOI_F2F1\u2019, \u2018VORONOI_CRACKLE\u2019, \u2018CELLNOISE\u2019].\n"], "Returns\nThe variable lacunarity noise value.\nReturn type\nfloat\n"], "voronoi()": ["Returns a list of distances to the four closest features and their locations.\n", ["position", "distance_metric", "exponent"], ["position (mathutils.Vector) \u2013 The position to evaluate the selected noise function.\n", "distance_metric (string) \u2013 Enumerator in [\u2018DISTANCE\u2019, \u2018DISTANCE_SQUARED\u2019, \u2018MANHATTAN\u2019, \u2018CHEBYCHEV\u2019, \u2018MINKOVSKY\u2019, \u2018MINKOVSKY_HALF\u2019, \u2018MINKOVSKY_FOUR\u2019].\n", "exponent (float) \u2013 The exponent for Minkowski distance metric.\n"], "Returns\nA list of distances to the four closest features and their locations.\nReturn type\nlist of four floats, list of four mathutils.Vector types"]}
types = []
for i,type in enumerate(dict_mathutils.keys()):
    types.append((type,type,dict_mathutils[type][0],i))

class SvMathuNoiseNode(SverchCustomTreeNode, bpy.types.Node):
    '''The Blender mathutils.noise module'''
    bl_idname = 'SvMathuNoiseNode'
    bl_label = 'Mathutils Noise'
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
        description = 'Operator of mathutils.noise',
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
                fun = 'mathutils.noise.' + self.oper[:-2] + '(' + param + ')'
                result.append(eval(fun))
            return_.append(result)
        return return_

def register():
    bpy.utils.register_class(SvMathuNoiseNode)


def unregister():
    bpy.utils.unregister_class(SvMathuNoiseNode)