bl_info = {
    "name": "blmaxbones",
    "description": "Copy animation between different armature by bone constrain",
    "author": "Jonas",
    "version": (1,0,1),
    "blender": (2, 83, 0),
    "location": "View 3D > Toolshelf",
    "doc_url": "",
    "tracker_url": "",
    "category": "Armature",
    }
import bpy, bmesh, math, re, operator, os, difflib, csv
from math import degrees, log2, pi, radians, ceil, sqrt
from bpy.types import Panel, UIList
import mathutils
from mathutils import Vector, Euler, Matrix
from bl_operators.presets import AddPresetBase

####################### DATA ##########################
RigDef = {
    #Body
    'Bip001 Pelvis':'DEF-spine',
    'Bip001 Spine':'DEF-spine.001',
    'Bip001 Spine1':'DEF-spine.002',
    'Bip001 Spine2':'DEF-spine.003',
    #Head
    'Bip001 Neck':'DEF-spine.004',
    'Bip001 Neck':'DEF-spine.005',
    'Bip001 Head':'DEF-spine.006', 
    #Left Arm
    'Bip001 L Clavicle':'ORG-shoulder.L',
    'Bip001 L UpperArm':'ORG-upper_arm.L',
    'Bip001 L Forearm':'ORG-forearm.L',
    'Bip001 L Hand':'ORG-hand.L',
    #Right Arm 
    'Bip001 R Clavicle':'ORG-shoulder.R',
    'Bip001 R UpperArm':'ORG-upper_arm.R',
    'Bip001 R Forearm':'ORG-forearm.R',
    'Bip001 R Hand':'ORG-hand.R',
    #Left Leg
    'Bip001 L Thigh':'ORG-thigh.L',
    'Bip001 L Calf':'ORG-shin.L',
    'Bip001 L Foot':'ORG-foot.L',
    'Bip001 L Toe0':'ORG-toe.L',
    #Right Leg
    'Bip001 R Thigh':'ORG-thigh.R',
    'Bip001 R Calf':'ORG-shin.R',
    'Bip001 R Foot':'ORG-foot.R',
    'Bip001 R Toe0':'ORG-toe.R',
    #Left Finger
    'Bip001 L Finger0':'DEF-thumb.01.L',
    'Bip001 L Finger01':'DEF-thumb.02.L',
    'Bip001 L Finger02':'DEF-thumb.03.L',
    'Bip001 L Finger1':'DEF-f_index.01.L',
    'Bip001 L Finger11':'DEF-f_index.02.L',
    'Bip001 L Finger12':'DEF-f_index.03.L',
    'Bip001 L Finger2':'DEF-f_middle.01.L',
    'Bip001 L Finger21':'DEF-f_middle.02.L',
    'Bip001 L Finger22':'DEF-f_middle.03.L',
    'Bip001 L Finger3':'DEF-f_ring.01.L',
    'Bip001 L Finger31':'DEF-f_ring.02.L',
    'Bip001 L Finger32':'DEF-f_ring.03.L',
    'Bip001 L Finger4':'DEF-f_pinky.01.L',
    'Bip001 L Finger41':'DEF-f_pinky.02.L',
    'Bip001 L Finger42':'DEF-f_pinky.03.L',
    #Right Finger
    'Bip001 R Finger0':'DEF-thumb.01.R',
    'Bip001 R Finger01':'DEF-thumb.02.R',
    'Bip001 R Finger02':'DEF-thumb.03.R',
    'Bip001 R Finger1':'DEF-f_index.01.R',
    'Bip001 R Finger11':'DEF-f_index.02.R',
    'Bip001 R Finger12':'DEF-f_index.03.R',
    'Bip001 R Finger2':'DEF-f_middRe.01.R',
    'Bip001 R Finger21':'DEF-f_middRe.02.R',
    'Bip001 R Finger22':'DEF-f_middRe.03.R',
    'Bip001 R Finger3':'DEF-f_ring.01.R',
    'Bip001 R Finger31':'DEF-f_ring.02.R',
    'Bip001 R Finger32':'DEF-f_ring.03.R',
    'Bip001 R Finger4':'DEF-f_pinky.01.R',
    'Bip001 R Finger41':'DEF-f_pinky.02.R',
    'Bip001 R Finger42':'DEF-f_pinky.03.R',
    #Deform bones
    'Bip001 LUpArmTwist':'DEF-upper_arm.L',
    'Bip001 LUpArmTwist1':'DEF-upper_arm.L.001',
    'Bip001 L ForeTwist':'DEF-forearm.L',
    'Bip001 L ForeTwist1':'DEF-forearm.L.001',

    'Bip001 RUpArmTwist':'DEF-upper_arm.R',
    'Bip001 RUpArmTwist1':'DEF-upper_arm.R.001',
    'Bip001 R ForeTwist':'DEF-forearm.R',
    'Bip001 R ForeTwist1':'DEF-forearm.R.001',

    'Bip001 LThighTwist':'DEF-thigh.L',
    'Bip001 LThighTwist1':'DEF-thigh.L.001',
    'Bip001 LCalfTwist':'DEF-shin.L',
    'Bip001 LCalfTwist1':'DEF-shin.L.001',

    'Bip001 RThighTwist':'DEF-thigh.R',
    'Bip001 RThighTwist1':'DEF-thigh.R.001',
    'Bip001 RCalfTwist':'DEF-shin.R',
    'Bip001 RCalfTwist1':'DEF-shin.R.001'
}

RigMax = {
    #Body
    'spine':'Bip001 Pelvis',
    'spine.001':'Bip001 Spine',
    'spine.002':'Bip001 Spine1',
    'spine.003':'Bip001 Spine2',
    #Head
    'spine.004':'Bip001 Neck',
    'spine.005':'Bip001 Neck',
    'spine.006':'Bip001 Head',
    #Left Arm
    'shoulder.L':'Bip001 L Clavicle',
    'upper_arm.L':'Bip001 L UpperArm',
    'forearm.L':'Bip001 L Forearm',
    'hand.L':'Bip001 L Hand',
    #Right Arm 
    'shoulder.R':'Bip001 R Clavicle',
    'upper_arm.R':'Bip001 R UpperArm',
    'forearm.R':'Bip001 R Forearm',
    'hand.R':'Bip001 R Hand', 
    #Left Leg
    'thigh.L':'Bip001 L Thigh',
    'shin.L':'Bip001 L Calf',
    'foot.L':'Bip001 L Foot',
    'toe.L':'Bip001 L Toe0',
    #Right Leg
    'thigh.R':'Bip001 R Thigh',
    'shin.R':'Bip001 R Calf',
    'foot.R':'Bip001 R Foot',
    'toe.R':'Bip001 R Toe0',
    #Left Finger
    'thumb.01.L':'Bip001 L Finger0',
    'thumb.02.L':'Bip001 L Finger01',
    'thumb.03.L':'Bip001 L Finger02',
    'f_index.01.L':'Bip001 L Finger1',
    'f_index.02.L':'Bip001 L Finger11',
    'f_index.03.L':'Bip001 L Finger12',
    'f_middle.01.L':'Bip001 L Finger2',
    'f_middle.02.L':'Bip001 L Finger21',
    'f_middle.03.L':'Bip001 L Finger22',
    'f_ring.01.L':'Bip001 L Finger3',
    'f_ring.02.L':'Bip001 L Finger31',
    'f_ring.03.L':'Bip001 L Finger32',
    'f_pinky.01.L':'Bip001 L Finger4',
    'f_pinky.02.L':'Bip001 L Finger41',
    'f_pinky.03.L':'Bip001 L Finger42',
    #Right Finger
    'thumb.01.R':'Bip001 R Finger0',
    'thumb.02.R':'Bip001 R Finger01',
    'thumb.03.R':'Bip001 R Finger02',
    'f_index.01.R':'Bip001 R Finger1',
    'f_index.02.R':'Bip001 R Finger11',
    'f_index.03.R':'Bip001 R Finger12',
    'f_middle.01.R':'Bip001 R Finger2',
    'f_middle.02.R':'Bip001 R Finger21',
    'f_middle.03.R':'Bip001 R Finger22',
    'f_ring.01.R':'Bip001 R Finger3',
    'f_ring.02.R':'Bip001 R Finger31',
    'f_ring.03.R':'Bip001 R Finger32',
    'f_pinky.01.R':'Bip001 R Finger4',
    'f_pinky.02.R':'Bip001 R Finger41',
    'f_pinky.03.R':'Bip001 R Finger42',
    #Other Four Hand
    'palm.01.L':'Bip001 L Hand',
    'palm.02.L':'Bip001 L Hand',
    'palm.03.L':'Bip001 L Hand',
    'palm.04.L':'Bip001 L Hand',
    'palm.01.R':'Bip001 R Hand',
    'palm.02.R':'Bip001 R Hand',
    'palm.03.R':'Bip001 R Hand',
    'palm.04.R':'Bip001 R Hand',  
}
# Tool bones deleted 
RigDele = [
    'face',
    'nose',
    'nose.001',
    'nose.002',
    'nose.003',
    'nose.004',
    'lip.T.L',
    'lip.T.L.001',
    'lip.B.L',
    'lip.B.L.001',
    'jaw',
    'chin',
    'chin.001',
    'ear.L',
    'ear.L.001',
    'ear.L.002',
    'ear.L.003',
    'ear.L.004',
    'ear.R',
    'ear.R.001',
    'ear.R.002',
    'ear.R.003',
    'ear.R.004',
    'lip.T.R',
    'lip.T.R.001',
    'lip.B.R',
    'lip.B.R.001',
    'brow.B.L',
    'brow.B.L.001',
    'brow.B.L.002',
    'brow.B.L.003',
    'lid.T.L',
    'lid.T.L.001',
    'lid.T.L.002',
    'lid.T.L.003',
    'lid.B.L',
    'lid.B.L.001',
    'lid.B.L.002',
    'lid.B.L.003',
    'brow.B.R',
    'brow.B.R.001',
    'brow.B.R.002',
    'brow.B.R.003',
    'lid.T.R',
    'lid.T.R.001',
    'lid.T.R.002',
    'lid.T.R.003',
    'lid.B.R',
    'lid.B.R.001',
    'lid.B.R.002',
    'lid.B.R.003',
    'forehead.L',
    'forehead.L.001',
    'forehead.L.002',
    'temple.L',
    'jaw.L',
    'jaw.L.001',
    'chin.L',
    'cheek.B.L',
    'cheek.B.L.001',
    'brow.T.L',
    'brow.T.L.001',
    'brow.T.L.002',
    'brow.T.L.003',
    'forehead.R',
    'forehead.R.001',
    'forehead.R.002',
    'temple.R',
    'jaw.R',
    'jaw.R.001',
    'chin.R',
    'cheek.B.R',
    'cheek.B.R.001',
    'brow.T.R',
    'brow.T.R.001',
    'brow.T.R.002',
    'brow.T.R.003',
    'eye.L',
    'eye.R',
    'cheek.T.L',
    'cheek.T.L.001',
    'nose.L',
    'nose.L.001',
    'cheek.T.R',
    'cheek.T.R.001',
    'nose.R',
    'nose.R.001',
    'teeth.T',
    'teeth.B',
    'tongue',
    'tongue.001',
    'tongue.002',
    'breast.L',
    'breast.R'
]

####################### OPERATOR CLASS ##########################
# 骨架资源的导入导出
class IM_OT_FBX(bpy.types.Operator):
    bl_idname="obj.import_fbx"
    bl_label="import bones"

    def execute(self,context):  
        bpy.ops.import_scene.fbx('INVOKE_DEFAULT',filepath="", directory="",
        filter_glob="*.fbx", files=[], ui_tab='MAIN', use_manual_orientation=False,
        global_scale=1, bake_space_transform=False, use_custom_normals=True,
        use_image_search=True, use_alpha_decals=False, decal_offset=0,use_anim=False,
        anim_offset=1,use_subsurf=False, use_custom_props=True, use_custom_props_enum_as_string=True,
        ignore_leaf_bones=True, force_connect_children=False, automatic_bone_orientation=False, 
        primary_bone_axis='X', secondary_bone_axis='Y', use_prepost_rot=True, axis_forward='-Z', axis_up='Y')

        return {'FINISHED'} 
class EX_OT_FBX(bpy.types.Operator):
    bl_idname="obj.export_fbx"
    bl_label="export bones"

    def execute(self,context):
        bpy.ops.export_scene.fbx('INVOKE_DEFAULT',filepath="", check_existing=True, filter_glob="*.fbx", 
        use_selection=True, use_active_collection=False, global_scale=1, apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE', bake_space_transform=False,
        object_types={'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'},
        use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF',
        use_subsurf=False, use_mesh_edges=False, use_tspace=False, use_custom_props=False, 
        add_leaf_bones=True, primary_bone_axis='X', secondary_bone_axis='Y', use_armature_deform_only=False,
        armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True,
        bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1,
        bake_anim_simplify_factor=1, path_mode='AUTO', embed_textures=False, batch_mode='OFF', 
        use_batch_own_dir=True, use_metadata=True, axis_forward='-Z', axis_up='Y')
 
        return {'FINISHED'} 




#Add Deleted bones 
class Tool_Addbones(bpy.types.Operator):
    bl_idname="obj.addbones"
    bl_label="add deleted bones "
    
   
    def execute(self,context):
         
        bpy.ops.object.armature_human_metarig_add()
      
        temp = bpy.context.active_object
        bpy.ops.object.mode_set(mode='EDIT')    
        if temp.type == 'ARMATURE':
            armature = temp.data
            
        #StructRNA of type EditBone has been removed  
        for i in RigDele:
            for bone in armature.edit_bones:
                if bone.name == i:
                    armature.edit_bones.remove(bone)
                    
        bpy.ops.object.mode_set(mode='OBJECT')
                  
        return {'FINISHED'} 
  
        
# 对其骨骼
class Rigbones(bpy.types.Operator):
    bl_idname="obj.rigbones"
    bl_label="To its bones"

    def execute(self,context):

        scn = context.scene
        obj = bpy.context.object

        ebones = bpy.data.armatures[scn.source_rig].edit_bones 
        #ebones = obj.data.edit_bones 
        maxrig = bpy.data.armatures[scn.target_rig].edit_bones
        
        bpy.data.objects[scn.source_rig].select_set(True) 
        bpy.data.objects[scn.target_rig].select_set(True) 

        if maxrig != None and ebones != None:

            if bpy.context.object.mode!='EDIF':
                bpy.ops.object.mode_set(mode='EDIT')

            try:
                for i,j in RigMax.items():              
                    ebones[i].head = maxrig[j].head
                    ebones[i].tail = maxrig[j].tail

                ebones['spine.003'].tail = ebones['spine.004'].head
                ebones['spine.004'].tail = (ebones['spine.005'].head + ebones['spine.005'].tail) / 2.0
                ebones['spine.005'].head = ebones['spine.004'].tail

                ebones['pelvis.L'].head = ebones['spine'].head
                ebones['pelvis.R'].head = ebones['spine'].head

                ebones['pelvis.L'].tail = (ebones['spine'].tail + ebones['thigh.L'].head)/2.0
                ebones['pelvis.R'].tail = (ebones['spine'].tail + ebones['thigh.R'].head)/2.0

                self.report({'INFO'}, "吸附成功!")
            except Exception as e:

                print('Missing relevant data',e)
                self.report({'INFO'}, "请让场景中只有一个rig骨骼!")
        else:
            self.report({'INFO'}, "请在对应框内填入相应选项!")
            
        #bpy.data.objects[scn.source_rig].select_set(False) 
        bpy.data.objects[scn.target_rig].select_set(False)     
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'} 

#生成控制
# 为第三方骨骼添加CO控制器
class CoBones(bpy.types.Operator):
    bl_idname="obj.cobones"
    bl_label="Detach bone hierarchy"

    @classmethod
    def poll(cls, context):
        return (context.scene.source_rig != "" and context.scene.target_rig != "")

    def execute(self,context):
        scn = context.scene

        copyclear()
        fast_mapping()

        if fast_mapping():
            self.report({'INFO'}, "映射成功！")
        
        return{'FINISHED'}


####################### UI  ##########################

class IE_PT_Panel(bpy.types.Panel):
    #bl_idname = "IEPanel"
    bl_label = "Skeleton Import And Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlMaxbones"
    
    def draw(self, context):
        #layout = self.layout
        #layout.scale_y = 1.2
        layout = self.layout.column(align=True)
        
        row = layout.row(align=True)
        #row = layout.row()
        row.operator("obj.import_fbx",text="导入")
        row.operator("import_scene.fbx",icon='PREFERENCES',text="")  
        
        row = layout.row(align=True)
        #row = layout.row()
        row.operator("obj.export_fbx",text="导出")  
        row.operator("export_scene.fbx",icon='PREFERENCES',text="")  
    
# 快捷键工具
class TOOLS_PT_Panel(bpy.types.Panel):
    bl_idname = "TOOLS_PT_Panel"
    bl_label = "工具栏"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlMaxbones"
    bl_parent_id = "RIG_PT_Panel"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout

        layout = self.layout.column(align=True)

        row = layout.row(align=True)
        row.operator("obj.rigbones",text="吸附骨架")
        row.operator("pose.rigify_generate",text="生成控制器")
        layout.separator()
        
        row = layout.row(align=True) 
        # row.operator("object.armature_add",text="Bone")
        row.operator("object.armature_human_metarig_add",text="Human(H)")
        #row = layout.row(align=True) 
        #row.operator("obj.scale",text="Scale")
        row.operator("obj.addbones",text="Human")         
        
        row = layout.row(align=True) 
        row.operator("object.transform_apply",icon='IPO_SINE',text="Apply")    

# Blender 骨架的一系列操作(吸附\rig\复制\约束)
class RIG_PT_Panel(bpy.types.Panel):
    bl_idname = "RIG_PT_Panel"
    bl_label = "Metarig Constraints"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlMaxbones"

    def draw(self, context):    
        layout = self.layout
        obj = context.object 
        scn = context.scene
      
        # Inputs
        layout = self.layout.column(align=True)
        
        row = layout.row(align=True) 
        row.column().label(text='Max 骨架(复制):')
        layout.separator()
        
        row = layout.row(align=True)
        
        row.prop_search(scn,'target_rig', bpy.data,'objects', text='')
        layout.separator()
      
        row = layout.row(align=True)
        row.column().label(text='Blender Rig骨架:')
        layout.separator()
        
        row = layout.row(align=True)
        row.prop_search(scn, 'source_rig',bpy.data,'objects', text='')
        layout.separator()
            
        row = layout.row(align=True) 
        row.column().label(text='添加控制器(快速):')
        layout.separator()

            
        row = layout.row(align=True)
        row.operator("obj.cobones",icon='CONSTRAINT_BONE',text="添加映射")
        
####################### FNC ##########################
#全局公用变量
#Global utilities---------------------------------------------------------


def copyclear():
    scn = bpy.context.scene
    # Check for duplicate copy bones
    if scn.copy_rig != None :
        try:
            #bpy.data.objects[scn.copy_rig].select_set(True) 
            #bpy.data.objects.remove(bpy.data.armatures[scn.copy_rig])
            bpy.data.objects.remove(bpy.data.objects[scn.copy_rig])  
            #bpy.ops.object.delete()
        except Exception as e:
            print('Missing relevant data',e)
    else:
        pass
    
    source_rig = get_object(scn.source_rig)  
    # Copy bones
    target_rig = get_object(scn.target_rig)   
    copy_rig = target_rig.copy() 
    copy_rig.data = target_rig.data.copy()
    copy_rig.name = target_rig.name + '_copy'
    copy_rig.data.name = target_rig.name + '_copy'
    bpy.context.collection.objects.link(copy_rig)     
    # Bone's parent_clear
    for obj in bpy.data.objects:
        obj.select_set(False)

    for ob in scn.objects:    
        if ob == target_rig :
            bpy.data.objects[scn.target_rig].select_set(False)
        elif ob == source_rig:
            bpy.data.objects[scn.source_rig].select_set(False)
        elif ob == copy_rig :
            bpy.context.view_layer.objects.active = ob
            if bpy.context.object.mode!='EDIF':
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.select_all(action='SELECT')
            bpy.ops.armature.parent_clear(type='CLEAR')
            bpy.ops.object.mode_set(mode='OBJECT')
      

    # return  
    scn.copy_rig = copy_rig.name
    return scn.copy_rig

def fast_mapping():
    scn = bpy.context.scene
    cpbones = bpy.data.objects[scn.copy_rig]
    blbones  = bpy.data.objects[scn.source_rig]

    # CHILD_OF
    if cpbones != None and blbones!= None:

        for bone in cpbones.pose.bones:
            for con in bone.constraints:
                bone.constraints.remove(con)
        try:
            for i,j in RigDef.items():
                copy_co = cpbones.pose.bones[i].constraints.new('CHILD_OF')
                copy_co.target = blbones
                copy_co.subtarget = j

        except Exception as e:
            print('Missing relevant data',e)

    # COPY_TRANSFORMS
    armatureFrom = bpy.data.objects[scn.copy_rig]
    armatureTo = bpy.data.objects[scn.target_rig]

    for boneTo in armatureTo.pose.bones:
        boneFrom = armatureFrom.pose.bones.get(boneTo.name)
        if boneFrom == None:
            continue
        for con in boneTo.constraints:
            boneTo.constraints.remove(con)

        copy_con = boneTo.constraints.new('COPY_TRANSFORMS')
        copy_con.target = armatureFrom
        copy_con.subtarget = boneFrom.name
        copy_con.target_space = 'WORLD'
        copy_con.owner_space = 'WORLD'

    return True
            



def get_edit_bone(name):
    return bpy.context.active_object.data.edit_bones.get(name)

def get_pose_bone(name):
    return bpy.context.active_object.pose.bones.get(name)


def entries_are_set():
    scn = bpy.context.scene
    if scn.source_rig != "" and scn.target_rig != "":
        return True
    else:
        return False




def get_object(obj_name):
    return bpy.data.objects.get(obj_name)

def set_global_scale(context):
    scn = context.scene
    source_rig = get_object(scn.source_rig)
    target_rig = get_object(scn.target_rig)
    copy_rig = get_object(scn.copy_rig)




def update_source_rig(self, context):   
    scn = context.scene
    # set source action
    if scn.source_rig != "":
        arm_obj = get_object(scn.source_rig)
    
    # set global scale
    if scn.source_rig != "" and scn.target_rig != "":
        set_global_scale(context)

def set_active_object(object_name):
     bpy.context.view_layer.objects.active = get_object(object_name)
     get_object(object_name).select_set(state=1)

def sanity_check(self):
    # check if both source and target armature are in the scene
    try:
        set_active_object(bpy.context.scene.source_rig)
        set_active_object(bpy.context.scene.target_rig)
        return True

    except:
        print("Armature not found")
        self.report({'ERROR'}, "Armature not found")
        return False



def update_target_rig(self,context):
    scn = context.scene    
    # set global scale
    if scn.source_rig != "" and scn.target_rig != "":
        set_global_scale(context)


def update_copy_rig(self,context):
    scn = context.scene    
    # set global scale
    if scn.source_rig != "" and scn.target_rig != "":
        set_global_scale(context)

# UI
class BCM_PT_Panel(bpy.types.Panel):
    bl_label = "Skeleton Mapping"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlMaxbones"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout  
        s = get_state()

        layout = self.layout.column(align=True)
        
        row = layout.row(align=True) 
        row.column().label(text='Max 骨架 :')
        row.column().label(text='Max 骨架(复制):')
        layout.separator()
    
        row = layout.row(align=True)
        row.prop(s, 'copy', text='', icon='OUTLINER_OB_ARMATURE')
        row.separator()
        row.prop(s, 'target', text='', icon='OUTLINER_OB_ARMATURE')
        
        layout.separator()

        row = layout.row(align=True)
        row.column().label(text='Blender Rig骨架:')
        layout.separator()

        row = layout.row(align=True)
        row.prop(s, 'source', text='', icon='OUTLINER_OB_ARMATURE')
        layout.separator(factor = 3)
              
        row = layout.row(align=True)
        row.label(text='使用预设:')

        row.menu(menu=BCM_MT_presets.__name__,text=BCM_MT_presets.bl_label)
        row.operator(AddPresetBCMMapping.bl_idname, text="", icon='ADD')
        row.operator(AddPresetBCMMapping.bl_idname, text="", icon='REMOVE').remove_active = True
        layout.separator(factor = 2)
    
        row = layout.row(align=True)
        split = row.split(factor=0.5)
        split.label(text="映射骨骼:")
        split.label(text="源头骨骼:")
        
        box = layout.box()
        row = box.row(align=True)
        row.template_list('BCM_UL_mappings', '', s, 'mappings', s, 'active_mapping')
        


        layout.separator(factor = 1)
        row = layout.split(align=True)
        row.operator('kumopult_bac.list_action', icon='ADD', text='').action = 'ADD'
        row.operator('kumopult_bac.list_action', icon='REMOVE', text='').action = 'REMOVE'

        row.operator('obj.listmax', icon='MENU_PANEL', text='')
        row.operator('obj.clearbones', icon='SNAP_NORMAL', text='')

        row = layout.row(align=True)
        row.operator('kumopult_bac.constraint_apply', text='映射')
     
        
class BCM_MT_presets(bpy.types.Menu):
    bl_label = "默认 Mapping"
    preset_subdir = "blender_max_bones"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset

class AddPresetBCMMapping(AddPresetBase, bpy.types.Operator):
    bl_idname = "kumopult_bac.mappings_preset_add"
    bl_label = "Add BCM Mappings Preset"
    bl_description = "add blender bones presets"
    preset_menu = "BCM_MT_presets"

    # variable used for all preset values
    # 用于所有预设值的变量
    preset_defines = [
        "s = bpy.context.scene.jonas"
    ]

    # properties to store in the preset
    # 要存储在预设中的属性
    preset_values = [
        "s.mappings"
    ]
    
    # 在何处存储预设
    # where to store the preset
    preset_subdir = "blender_max_bones"

# 自定义数据属性 
class BCM_BoneMapping(bpy.types.PropertyGroup):

    source: bpy.props.StringProperty()
    target: bpy.props.StringProperty()
    copy: bpy.props.StringProperty()
    
    def apply_bone(self):

        cf = self.add_child_of()
        ct = self.add_copy_trans()
 
# ----------------- 添加Child of控制器 ---------------
    def add_child_of(self):   
        j = get_state()

        armatureFrom = j.target.pose.bones[self.target].constraints   
        # armatureTo = j.target

        # for boneTo in armatureTo.pose.bones:
        #     for con in boneTo.constraints:
        #         boneTo.constraints.remove(con)
 
        cf = armatureFrom.new(type='CHILD_OF')
        cf.target = get_state().source
        cf.subtarget = self.source 

        return cf
 
# --------------- 添加copy_trans控制器 ---------------
    def add_copy_trans(self):
        j = get_state()

        armatureFrom = j.target
        armatureTo = j.copy

        for boneTo in armatureTo.pose.bones:
            boneFrom = armatureFrom.pose.bones.get(boneTo.name)
            if boneFrom == None:
                continue
            for con in boneTo.constraints:
                boneTo.constraints.remove(con)

            ct = boneTo.constraints.new('COPY_TRANSFORMS')
            ct.target = armatureFrom
            ct.subtarget = boneFrom.name
            ct.target_space = 'WORLD'
            ct.owner_space = 'WORLD'

        return ct


    def con_list(self):
        return {
            self.add_child_of: False,
            self.add_copy_trans: False
        }


    def clear(self):
        for key, value in self.con_list().items():
            if value:
                self.remove(key())

    def remove(self, constraint):

        get_state().get_target_pose().bones.get(self.target).constraints.remove(constraint)

class BCM_State(bpy.types.PropertyGroup):
    
    source: bpy.props.PointerProperty(type=bpy.types.Object)
    target: bpy.props.PointerProperty(type=bpy.types.Object)
    copy: bpy.props.PointerProperty(type=bpy.types.Object)

    mappings: bpy.props.CollectionProperty(type=BCM_BoneMapping)

    active_mapping: bpy.props.IntProperty(default=-1)

    def get_target_pose(self):
        return self.target.pose

    def get_source_armature(self):
        return self.source.data

    def get_target_armature(self):
        return self.target.data

    def get_mapping_by_target(self, name):
        if name != "":
            for i, m in enumerate(self.mappings):
                if m.target == name:
                    return m, i
        return None, -1
    
    # 添加映射
    def add_mapping(self, target, source, copy):

        m,i = self.get_mapping_by_target(target)
        # 若已存在，则覆盖原本的源骨骼，并返回映射和索引值
        if m:
            print("目标骨骼已存在映射关系，已覆盖修改源骨骼")
            m.source = source
            return m,i

        m = self.mappings.add()
        m.target = target
        m.copy = copy
        m.source = source
        return m,len(self.mappings) - 1

    def add_mapping_below(self, target, source, copy):
        i = self.add_mapping(target, source,copy)[1]
        self.mappings.move(i, self.active_mapping + 1)
        self.active_mapping += 1

    def remove_mapping(self, index):

        self.mappings[index].clear()
        self.mappings.remove(index)


# mapping 映射
class BCM_UL_mappings(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        s = get_state()
        layout.prop_search(item, 'target', s.get_target_armature(), 'bones', text='', icon='BONE_DATA')
        layout.label(icon='RIGHTARROW_THIN')
        layout.prop_search(item, 'source', s.get_source_armature(), 'bones', text='', icon='BONE_DATA')
        layout.operator("arp.pick_object", text="", icon='EYEDROPPER').action = 'pick_bone'

    # def invoke(self, context, event):
    #     pass
  
# 拾取所选对象/骨骼
class ARP_OT_pick_object(bpy.types.Operator):

    # tooltip
    # 拾取所选对象/骨骼
    """Pick the selected object/bone"""

    bl_idname = "arp.pick_object"
    bl_label = "pick_object"
    bl_options = {'UNDO'}

    action : bpy.props.EnumProperty(
        items=(
                ('pick_source', 'pick_source', ''),
                ('pick_target', 'pick_target', ''),
                ('pick_bone', 'pick_bone', ''),
                ('pick_pole', 'pick_pole', '')
            )
        )

    @classmethod
    def poll(cls, context):
        return (context.active_object != None)

    def execute(self, context):
        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False

        try:
            _pick_object(self.action)
        finally:
            context.preferences.edit.use_global_undo = use_global_undo

        return {'FINISHED'}


           
def _pick_object(action):
    obj = bpy.context.object
    scene = bpy.context.scene
    s = get_state()

    if action == "pick_source":
        scene.source_rig = obj.name
    if action == "pick_target":
        scene.target_rig = obj.name
    if action == 'pick_bone':
        try:
            pose_bones = obj.pose.bones
            #scene.bones_map[scene.bones_map_index].name = bpy.context.active_pose_bone.name
            s.mappings[s.active_mapping].source = bpy.context.active_pose_bone.name
            ww = bpy.context.active_pose_bone.name
            print(ww)
        except:
            print("can't pick bone")

    if action == 'pick_pole':
        try:
            pose_bones = obj.pose.bones
        except:
            print("can't pick bone")

class BCM_OT_ClearBones(bpy.types.Operator):
    bl_idname = 'obj.clearbones'
    bl_label = 'clear'

    def execute(self, context):
        s = get_state()     

        if len(s.mappings) > 0:
            i = len(s.mappings)
            while i >= 0:
                s.mappings.remove(i)
                i -= 1
        return {'FINISHED'}



class BCM_OT_ListMax(bpy.types.Operator):
    bl_idname = 'obj.listmax'
    bl_label = 'list'


    def execute(self, context):
        s = get_state()     

    
        if len(s.mappings) > 0:
            i = len(s.mappings)
            while i >= 0:
                s.mappings.remove(i)
                i -= 1
        if s.target != None:
            for i in s.target.pose.bones:
                s.add_mapping(i.name,'','')
        else:
            self.report({'INFO'}, "请选择相应骨架！")

            
    

        return {'FINISHED'}

# def add_mapping_below(target, source, copy):
#     s = get_state()
#     if not s.add_mapping(target, source, copy):
#         return
#     s.mappings.move(len(s.mappings) - 1, s.active_mapping + 1)
#     s.active_mapping += 1


class BCM_OT_ListAction(bpy.types.Operator):
    bl_idname = 'kumopult_bac.list_action'
    bl_label = '列表基本操作'
    bl_description = '依次为新建、删除、上移、下移\n其中在姿态模式下选中骨骼并点击新建的话，\n可以自动填入对应骨骼'
    action: bpy.props.StringProperty()

    def execute(self, context):
        s = get_state()

        def add():
            #这里需要加一下判断，如果有选中的骨骼则自动填入target
            #pb = bpy.context.selected_pose_bones_from_active_object
            pb = bpy.context.selected_pose_bones

            se_target = ''
            se_source = ''


            if pb != None and len(pb) == 1:
                #selection_names = {}
                for j in bpy.context.selected_pose_bones:
                    
                    if j.id_data.name == s.copy.name:
                        se_target = j.name
                        s.add_mapping_below(se_target,'',se_target)

                    if j.id_data.name == s.source.name:
                        se_source = j.name
                        s.add_mapping_below('',se_source,'')

                
            elif  pb != None and len(pb) > 1:
    
                for j in bpy.context.selected_pose_bones:
                    
                    if j.id_data.name == s.copy.name:
                        se_target = j.name

                    if j.id_data.name == s.source.name:
                        se_source = j.name

                s.add_mapping_below(se_target,se_source,se_target)

            # if bpy.context.selected_pose_bones != None:
            #     selection_names = []
            #     for obj in bpy.context.selected_pose_bones:
            #         selection_names.append(obj.name)
            else:
                s.add_mapping_below('', '','')
        
        def remove():
            if len(s.mappings) > 0:
                if s.active_mapping != None :
                    try:
                        s.remove_mapping(s.active_mapping)
                        s.active_mapping =  min(s.active_mapping, len(s.mappings) - 1)
                    except Exception as e:
                        self.report({'INFO'}, "请选择骨架列表!")
                else:
                    print("删除错误！")

            
        
        ops = {
            'ADD': add,
            'REMOVE': remove,
        }

        ops[self.action]()

        return {'FINISHED'}



# 执行映射 
class BCM_OT_Apply(bpy.types.Operator):
    bl_idname = 'kumopult_bac.constraint_apply'
    bl_label = 'Apply'
    
    def execute(self, context):

        s = get_state()
        armatureTo = s.target

        for boneTo in armatureTo.pose.bones:
            for con in boneTo.constraints:
                boneTo.constraints.remove(con)
 
        for mapping in s.mappings:
                mapping.apply_bone()
            
        return {'FINISHED'}
    


# utils
def get_state():
    return bpy.context.scene.jonas

classes = (
    

    BCM_OT_ClearBones,
    
    BCM_OT_ListMax,

    IM_OT_FBX,
    EX_OT_FBX,
    BCM_BoneMapping,
    BCM_State,    
    BCM_MT_presets,
    AddPresetBCMMapping,

    ARP_OT_pick_object,

    BCM_UL_mappings,
    BCM_OT_ListAction,

    BCM_OT_Apply,

   
    Tool_Addbones,
   
    Rigbones,
    CoBones,
   
 

    IE_PT_Panel,
    RIG_PT_Panel,
    TOOLS_PT_Panel,
    BCM_PT_Panel, 

    )

# register, unregister = bpy.utils.register_classes_factory(classes)

# Register
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.jonas = bpy.props.PointerProperty(type=BCM_State)
    bpy.types.Scene.target_rig = bpy.props.StringProperty(name = "Target Rig", default="", description="编辑外部导入的max骨架", update=update_target_rig)
    bpy.types.Scene.source_rig = bpy.props.StringProperty(name = "Source Rig", default="", description="", update=update_source_rig)
    bpy.types.Scene.copy_rig = bpy.props.StringProperty(name = "Blender Rig", default="", description="Source rig armature to take action from", update=update_copy_rig)



# Unregister
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.jonas
    del bpy.types.Scene.target_rig
    del bpy.types.Scene.source_rig
    del bpy.types.Scene.copy_rig
  


if __name__ == "__main__":
    register()