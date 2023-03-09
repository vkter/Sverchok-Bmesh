from bpy import context as C
from bpy.utils import register_classes_factory
from bpy.props import EnumProperty, BoolProperty
from bpy.types import Node
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from sverchok.utils.listutils import joiner
from mathutils import Vector,Matrix
import bmesh.ops
from time import time

class SvBmeshOpsLiteNode(SverchCustomTreeNode, Node):
    """
    Lite Operators for bmesh processing
    """
    bl_idname = 'SvBmeshOpsLiteNode'
    bl_label = 'BMesh Ops Lite'
    bl_icon = 'EDITMODE_HLT'

    def get_vars(self,function):
        doc=str((getattr(bmesh.ops,function).__doc__,))
        doc=doc[doc.index('(')+1:doc.find('\\')-1];doc=doc[doc.index('(')+1:]
        pairs=doc.split(',')
        for idx,item in enumerate(pairs):
            if 'custom' in item.lower():
                pairs.pop(idx)
        pairs=[param.replace(' ','').split('=') for param in pairs]
        pairs.pop(0)
        _vars=[param[0].capitalize().replace('_',' ') for param in pairs]
        _types=[param[1] for param in pairs]
        
        return zip(_vars,_types)
            
        
    def adaptive_sockets(self,enum_name):
        [self.safe_socket_remove('inputs',i) for i in self.inputs.keys() if i.lower()!='bmesh']
        for param,kind in self.get_vars(enum_name):
            ptype=eval(kind)
            #Matching the socket types
            if isinstance(ptype,(float,int)):
                inp=self.inputs.new('SvStringsSocket',param)
                if isinstance(ptype,(float)):
                    inp.default_property_type='float'
                    inp.use_prop=True
                else:
                    inp.default_property_type='int'
                    inp.use_prop=True

            elif isinstance(ptype,Matrix):
                self.inputs.new('SvMatrixSocket',param)
            
            elif isinstance(ptype,Vector):
                self.inputs.new('SvVerticesSocket',param).use_prop=True
                
            elif isinstance(ptype,str):
                inp=self.inputs.new('SvTextSocket',param)
                inp.default_property=str(kind)[1:-1]
                inp.use_prop=True
            else:
                inp=self.inputs.new('SvStringsSocket',param)
                inp.quick_link_to_node='SvListInputNode'
                
        #Moving Matrix sockets to the bottom       
        data_types=[i.bl_idname for i in self.inputs[:]]
        for _name,_type in zip(self.inputs.keys(),data_types):
            if _type=='SvMatrixSocket':
                self.inputs.move(self.inputs[_name].index,int(len(self.inputs[:])-1))
        self._update()        
                
    @property          
    def bm_functions(self):
        func=[]
        if self.inputs[0].other.node.bl_idname==self.bl_idname:
            func=self.inputs[0].other.node.bm_functions
        func.append((self,self.geom_ops))
        return func
    
    def use_index_or_mask(self,indexes,category,default_amount=6,use_default=True):
        category.ensure_lookup_table()
        if indexes:
            if isinstance(indexes[0],bool):
                return [category[ind] for ind,_cond in enumerate(indexes) if _cond]
            
            elif isinstance(indexes[0],int):
                return [category[ind] for ind in indexes]
        
        else:
            if use_default:
                return [category[ind] for ind in range(default_amount)]
            else:
                return []
    
    

    @property
    def input_node(self):
        node=self.inputs[0].other.node
        if node.bl_idname!=self.bl_idname:
            return node
        elif node.bl_idname==self.bl_idname:
            return node.input_node        
        
        
    def get_last_node(self):
        node=self.outputs[0].other
        if node:
            node=node.node
            while node.bl_idname==self.bl_idname:
                node=node.outputs[0].other.node
                if node.bl_idname!=self.bl_idname:
                    break
            return node.inputs[0].other.node
        else:
            raise Exception('Current node is not linked')
    
    
    def _update(self):
        updateNode(self,C)
        node=self.get_last_node()
        if node!=self:
            updateNode(node,C)
        
        
    def idx_update(self,context):
        for out in self.outputs[2:]:
            if not getattr(self,'calc_'+out.name[:5].lower().strip(' ')):
                if not out.hide_safe:
                    out.hide_safe=True
            elif getattr(self,'calc_'+out.name[:5].lower().strip(' ')):
                if out.hide_safe:
                    out.hide_safe=False  
        
    def _calc_update(self,context):
        if self.calculate_indices==False:
            for out in self.outputs[2:]:
                if not out.hide_safe:
                    out.hide_safe=True
                      
        
    def context_options(self,context):
        vertex=[(i,i.capitalize().replace('_',' '),"") for i  in sorted(['average_vert_facedata','connect_verts','connect_vert_pair','connect_verts_nonplanar','extrude_vert_indiv','find_doubles','smooth_vert','smooth_laplacian_vert','dissolve_verts','pointmerge','pointmerge_facedata','remove_doubles','unsubdivide','weld_verts'])]
        face=[(i,i.capitalize().replace('_',' '),"") for i in sorted(['connect_verts_concave','dissolve_faces','extrude_discrete_faces','extrude_face_region','face_attribute_fill','inset_individual','inset_region','join_triangles','planar_faces','poke','recalc_face_normals','reverse_faces','triangulate','wireframe','beautify_fill','reverse_colors','rotate_colors','rotate_uvs'])]
        edge=[(i,i.capitalize().replace('_',' '),"") for i in sorted(['bevel','bisect_edges','collapse','bridge_loops','dissolve_edges','edgeloop_fill','edgenet_fill','edgenet_prepare','extrude_edge_only','offset_edgeloops','rotate_edges','split_edges','subdivide_edgering','subdivide_edges','triangle_fill','grid_fill','holes_fill'])]
        base=[(i,i.capitalize().replace('_',' '),"") for i in sorted(['contextual_create','convex_hull','delete','duplicate','mirror','region_extend','solidify','spin','split','symmetrize','scale','transform','translate','rotate'])]
        create=[('create_'+i,i.capitalize(),"Create "+i,'MESH_'+i.upper(),idx) for idx,i  in enumerate(['cube','circle','cone','grid','icosphere','uvsphere','monkey'])]
        return locals()[self.bm_category]
    
        

    bmesh_buffers: {}
    bm_category: EnumProperty(items=[('create','Create','Create a BMesh primitive','OUTLINER_OB_MESH',0),('base','Base','Operations editing the BMesh Object as a whole','EDITMODE_HLT',1),('vertex','Vertex','Edit vertices of a Bmesh object','VERTEXSEL',2),('edge','Edge','Edit edges of a Bmesh object','EDGESEL',3),('face','Face','Edit faces of a Bmesh object','FACESEL',4)],\
                              description='Geometry context for operation',update=lambda self,context: self.adaptive_sockets(self.geom_ops),default=0)
    general_category: EnumProperty(items=__annotations__['bm_category'].keywords['items'][2:],update=updateNode)
    geom_ops: EnumProperty(items=context_options,update=__annotations__['bm_category'].keywords['update'],default=0,description='Geometry operation')
    calculate_indices: BoolProperty(name='Calculate indices',description='Calculate the indices of newly created geometry(if any)\n' 'Check N-Panel if True',update=_calc_update)
    calc_verts: BoolProperty(name='vert indices',description='Calculate the indices of newly created verts (if any)',update=idx_update)
    calc_edges: BoolProperty(name='edge indices',description='Calculate the indices of newly created edges (if any)',update=idx_update)
    calc_faces: BoolProperty(name='face indices',description='Calculate the indices of newly created faces (if any)',update=idx_update)
    calc_geom: BoolProperty(name='geom indices',description='Calculate the indices of newly created geometry (if any)',update=idx_update)
    
    def sv_init(self,context):
        inp1=self.inputs.new('SvStringsSocket','Bmesh')
        inp1.display_shape='DIAMOND_DOT'
        inp1.quick_link_to_node='SvBMInNode'
        out1=self.outputs.new('SvStringsSocket','Bmesh')
        out1.display_shape='DIAMOND_DOT'
        self.outputs.new('SvDictionarySocket','New Geom')
        self.outputs.new('SvStringsSocket','Geom (Indices)').hide_safe=True
        self.outputs.new('SvStringsSocket','Verts (Indices)').hide_safe=True
        self.outputs.new('SvStringsSocket','Edges (Indices)').hide_safe=True
        self.outputs.new('SvStringsSocket','Faces (Indices)').hide_safe=True
        self.geom_ops='create_cube'
        
    def process(self):
        buffs=self.__annotations__['bmesh_buffers']
        mandate=all([self.inputs[0].is_linked,self.outputs[0].is_linked])        
        if mandate and getattr(self.outputs[0].other,'node',self).bl_idname!=self.bl_idname:
            org_bm=joiner(self.input_node.outputs[0].sv_get(),1)[0]
            bm=org_bm.copy()
            bm_dict={'verts':bm.verts,'edges':bm.edges,'faces':bm.faces}   
            for node,func_name in self.bm_functions:
                [el.ensure_lookup_table() for el in [bm.verts,bm.faces,bm.edges]]
                parameters=''
                for var, kind in node.get_vars(node.geom_ops):
                    var_name=var.lower().replace(' ','_')
                    ptype=eval(kind)
                    parameters+=var_name+'='+var_name+','
                    try:
                        param_value=joiner(node.inputs[var].sv_get(),1)
                        if isinstance(param_value,list) and not isinstance(ptype,list):
                            param_value=param_value[0]
                    except:
                        param_value=ptype
                     
                    if isinstance(ptype,list):
                        if var_name in ['geom','input']:
                            param_value=self.use_index_or_mask(param_value,bm_dict[self.general_category[:4]+'s'],default_amount=locals()[self.general_category[:4]+'_len'])
          
                        elif var_name[:5] in bm_dict.keys():
                           param_value=self.use_index_or_mask(param_value,bm_dict[var_name[:5]],default_amount=locals()[var_name[:4]+'_len'],use_default=(True if var_name in bm_dict.keys() else False))
             
                    locals()[var_name]=param_value
                    
                locals().update()
                out_val=eval(f'bmesh.ops.{func_name}(bm,'+parameters[:-1]+')')
                node.outputs[0].sv_set([bm])
                node.outputs[1].sv_set([out_val])
                
                if node.calculate_indices and out_val:
                    for _name,_vals in out_val.items():
                        out=node.outputs[_name.capitalize()+' (Indices)']
                        out.sv_set([[el.index for el in _vals]])
    
                                 
                vert_len=len(bm.verts[:])
                edge_len=len(bm.edges[:])
                face_len=len(bm.faces[:])
                
            inp_name=self.input_node.name
            if inp_name not in buffs.keys():
                buffs[inp_name]=[bm]
            else:
                buffs[inp_name].append(bm)       
            if len(buffs[inp_name])>1:
                del buffs[inp_name][0]

        elif mandate:
            try:
                obj=self.outputs[0].sv_get()[0]
            except:
                obj=[]   
            self.outputs[0].sv_set([obj,[int(time())]])
 
        
    def draw_buttons(self,context,layout):
        update_func = 'node.scriptlite_ui_callback'
        a=layout.row(align=True)
        a.prop(self,'bm_category',text="")
        op=a.operator(update_func,icon='FILE_REFRESH',text='')
        op.fn_name='_update'
        r=layout.row(align=True)
        r.prop(self,'geom_ops',text='')
        r.prop(self,'calculate_indices',icon='LINENUMBERS_ON',icon_only=True)
        
        
        
    def draw_buttons_ext(self,context,layout):
        if self.bm_category!='create':
            layout.prop(self,'general_category',text='Context')
        if self.calculate_indices:
            layout.prop(self,'calc_verts',icon='VERTEXSEL')
            layout.prop(self,'calc_edges',icon='EDGESEL')
            layout.prop(self,'calc_faces',icon='FACESEL')
            layout.prop(self,'calc_geom',icon='OUTLINER_OB_MESH')
    
            
register, unregister=register_classes_factory([SvBmeshOpsLiteNode])
