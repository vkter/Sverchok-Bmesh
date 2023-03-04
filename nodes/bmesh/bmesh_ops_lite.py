from bpy.utils import register_classes_factory
from bpy.props import EnumProperty, BoolProperty, IntProperty
from bpy.types import Node
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from sverchok.utils.listutils import joiner
from mathutils import Vector,Matrix
import bmesh.ops

class SvBmeshOpsLiteNode(SverchCustomTreeNode, Node):
    """
    Lite Operators for bmesh processing
    """
    bl_idname = 'SvBmeshOpsLiteNode'
    bl_label = 'BMesh Ops Lite'
    bl_icon = 'EDIT'

    def get_vars(self,function):
        doc=str((eval(f'bmesh.ops.{function}.__doc__'),))
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
                
                
    def exec_function(self,bm,func_name,geom_context='verts'):
        bm_dict={'verts':bm.verts,'edges':bm.edges,'faces':bm.faces}
       
        def use_index_or_mask(self,indexes,cat,context,use_default=True):
            cat.ensure_lookup_table()
            if indexes:
                if isinstance(indexes[0],bool):
                    return [cat[ind] for ind,_cond in enumerate(indexes) if _cond]
                
                else:
                    return [cat[int(ind)] for ind in indexes]
            
            else:
                if use_default:
                    prev_bm=self.__annotations__['bmesh_objects'][-1]
                    prev_bm_dict={'verts':prev_bm.verts,'edges':prev_bm.edges,'faces':prev_bm.faces}
                    prev_bm_dict[context].ensure_lookup_table()
                      
                    return [cat[i] for i in range(len(prev_bm_dict[context][:]))]
                else:
                    return []
                
        parameters=''
        
        for var, kind in self.get_vars(func_name):
            var_name=var.lower().replace(' ','_')
            ptype=eval(kind)
            parameters+=var_name+'='+var_name+','
            try:
                param_value=joiner(self.inputs[var].sv_get(),1)
                if isinstance(param_value,(list)) and not isinstance(ptype,(list)):
                    param_value=param_value[0]
            except:
                param_value=ptype
             
            if isinstance(ptype,(list,tuple)):
                if var_name in ['geom','input']:
                    param_value=use_index_or_mask(self,param_value,bm_dict[geom_context],geom_context)
  
                elif var_name[:5] in bm_dict.keys():
                    param_value=use_index_or_mask(self,param_value,bm_dict[var_name[:5]],var_name,use_default=True if var_name in bm_dict.keys() else False)
     
            locals()[var_name]=param_value
            
        locals().update()
        return eval(f'bmesh.ops.{func_name}(bm,'+parameters[:-1]+')')
        
        
    def enum_update(self,context):
        self.adaptive_sockets(self.geom_ops)
        updateNode(self,context)
        
        
    def context_options(self,context):
        vertex=[(i,i.capitalize().replace('_',' '),"") for i  in sorted(['average_vert_facedata','collapse','connect_verts','connect_vert_pair','connect_verts_nonplanar','extrude_vert_indiv','find_doubles','smooth_vert','smooth_laplacian_vert','dissolve_verts','pointmerge','pointmerge_facedata','remove_doubles','scale','transform','translate','unsubdivide','weld_verts','rotate'])]
        face=[(i,i.capitalize().replace('_',' '),"") for i in sorted(['connect_verts_concave','dissolve_faces','extrude_discrete_faces','extrude_face_region','face_attribute_fill','inset_individual','inset_region','join_triangles','planar_faces','poke','recalc_face_normals','reverse_faces','triangulate','wireframe','beautify_fill','reverse_colors','rotate_colors','rotate_uvs'])]
        edge=[(i,i.capitalize().replace('_',' '),"") for i in sorted(['bevel','bisect_edges','bridge_loops','dissolve_edges','edgeloop_fill','edgenet_fill','edgenet_prepare','extrude_edge_only','offset_edgeloops','rotate_edges','split_edges','subdivide_edgering','subdivide_edges','triangle_fill','grid_fill','holes_fill'])]
        base=[(i,i.capitalize().replace('_',' '),"") for i in sorted(['contextual_create','convex_hull','delete','duplicate','mirror','region_extend','solidify','spin','split','symmetrize'])]
        create=[('create_'+i,i.capitalize(),"Create "+i,'MESH_'+i.upper(),idx) for idx,i  in enumerate(['cube','circle','icosphere','uvsphere','monkey','cone'])]
        return locals()[self.bm_category]
    
   
    operation_categories=[('create','Create','Create a BMesh primitive','OUTLINER_OB_MESH',0),('vertex','Vertex','Edit vertices of a Bmesh object','VERTEXSEL',1),('edge','Edge','Edit edges of a Bmesh object','EDGESEL',2),('face','Face','Edit faces of a Bmesh object','FACESEL',3),('base','Base','Operations editing the BMesh','EDIT',4)]
    bmesh_objects: []
    bmesh_buffers: list()
    bm_category: EnumProperty(items=operation_categories,description='Geometry context for operation',update=enum_update,default=0)
    general_category: EnumProperty(items=operation_categories[1:4],update=updateNode)
    geom_ops: EnumProperty(items=context_options,update=enum_update,default=0,description='Geometry operation')
    calculate_indices: BoolProperty(name='Calculate indices',description='Calculate the indices of newly created geometry(if any)',update=updateNode)
    
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
        self.enum_update(context)
        
     def process(self):
        bmesh_objects=self.__annotations__['bmesh_objects']
        bmesh_buffers=self.__annotations__['bmesh_buffers']
        if self.inputs[0].is_linked and self.outputs[0].is_linked:
            inp_val=self.inputs[0].sv_get()[0]
                
            try:
                inp_val.verts
                if not inp_val in bmesh_objects:
                    bmesh_objects.append(inp_val)
                    self.__annotations__.update()

            except ReferenceError:
                pass
            
            buff_bm=bmesh_objects[-1].copy()
            bmesh_buffers.append(buff_bm)

            option=self.general_category[:4]+'s'    
            ret=self.exec_function(buff_bm,self.geom_ops,geom_context=option)
            self.outputs[0].sv_set([buff_bm])
            self.outputs[1].sv_set([ret])
            if ret:
                for _name,_vals in ret.items():
                    out=self.outputs[_name.capitalize()+' (Indicies)']
                    out.hide=False
                    _val_indexes=[]
                    for val in _vals:
                        _val_indexes.append(val.index)
                    out.sv_set([_val_indexes])
                    
            for out in self.outputs:
                try:
                    out.sv_get()
                except:
                    out.hide_safe=True
            
            if len(bmesh_buffers)>1:
                del bmesh_buffers[0]

            if len(bmesh_objects)>1:
                bmesh_objects[0].free()
                del bmesh_objects[0]
                self.__annotations__.update()
            
                
    def draw_buttons(self,context,layout):
        layout.prop(self,'bm_category',text="")
        r=layout.row(align=True)
        r.prop(self,'geom_ops',text="")
        r.prop(self,'calculate_indices',icon='SAMPLE_INDEX',icon_only=True)
        
        
    def draw_buttons_ext(self,context,layout):
        if self.bm_category!='create':
            layout.prop(self,'general_category',text='Context')
            
        
classes=[SvBmeshOpsLiteNode]
register, unregister=register_classes_factory(classes)
