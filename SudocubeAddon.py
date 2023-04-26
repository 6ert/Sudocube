#######################################################################################
## Title: SudocubeAddon
## Author: Gert Weber • info@weberlebt.de • https://weberlebt.de • 2023
## License: CC BY lizenz • Namensnennung 2.0 Deutschland (CC BY 2.0 DE) • https://creativecommons.org/licenses/by/2.0/de/legalcode
## Blender: Blender is released under the GNU General Public License • http://download.blender.org/release/GPL-license.txt
## Disclaimer: The author makes no representations or warranties about the non-infringement or absence of other defects concerning the CC-licensed work.
#######################################################################################
bl_info = {
    "name": "Sudocube Addon",
    "author": "Gert Weber",
    "version": (1, 0),
    "blender": (3, 3, 1),
    "location": "SpaceBar Search -> Add-on Prefs",
    "description": "Sudocube Add-on",
    "warning": "",
    "doc_url": "",
    "tracker_url": "www.weberlebt.de",
    "category": "Object",
}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty
import mathutils
import random
import time
import os

############### PathPanel #################
class PathPanel(bpy.types.Panel):
    """Creates FilePath Panel in View-3D - Sidebar(shortcut: N) - Sudocube"""
    bl_idname = "OBJECT_PT_pathpanel"
    bl_label = "Image Path"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Sudocube"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        info = context.preferences.addons[__name__].preferences.filepath
        if info == "":
            row.label(text="Edit Piath in Addon Prefs!")          
        else:
            row.label(text=info)


############### SudoCubePanel #################
class SudoCubePanel(bpy.types.Panel):
    """Creates Game Panel in View-3D - Sidebar(shortcut: N) - Sudocube"""
    bl_label = "S U D O C U B E"
    bl_idname = "OBJECT_PT_sudocube"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Sudocube"
    
    def draw(self, context):
        layout = self.layout
        
        # if context.scene.sudocube_path.path == "":
        if context.preferences.addons[__name__].preferences.filepath == "":
            return None           

        GameID = len(bpy.context.scene.score_data)

        row = layout.row()
        row.label(text="SudoCube", icon='MESH_CUBE')
        
        row.label(text="Game:%s" % (GameID))

        row = layout.row()
        row.operator("wm.sudocubegame", icon='META_CUBE')

        row = layout.row()
        row.label(text="Im/Explode Sudocube:")                             
        if context.object.scale[0] < 1.0:
            layout.operator("properties.explode_operator", text="Implode SudoCube", icon='ZOOM_ALL')
        else:
            layout.operator("properties.explode_operator", text="Explode SudoCube", icon='ZOOM_IN')

        row = layout.row()
        row.label(text="Active Cube is: " + context.object.name)

        row = layout.row()
        row.label(text="assign | material | assigned")
        
        row = layout.row()
        row.template_ID(context.object, "active_material")
        
        if GameID > 0:
            row = layout.row()
            row.label(text="Time: %s" % time.strftime("%H:%M:%S", time.gmtime(bpy.context.scene.score_data[GameID-1].duration)))   #, icon='WORLD_DATA')

            row = layout.row()
            percent = int(bpy.context.scene.score_data[GameID-1].progress/1.35)
            row.label(text="Progress: %s" % str(percent)+'%')
            
            if bpy.context.scene.score_data[GameID-1].progress == 135:
                row = layout.row()
                row.label(text="FINISHED Score: %s" % str(int(bpy.context.scene.score_data[GameID-1].plusscore)))
                row = layout.row()
                row.label(text="Total Score: %s" % str(bpy.context.scene.score_data[GameID-1].score_total))

############### ExplodeOperator #################
class ExplodeOperator(bpy.types.Operator):
    """ SudoCube im/exploded State """
    bl_idname = "properties.explode_operator"
    bl_label = "Explode Properties Operator"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'
        
    # @classmethod
    def execute(self, context):
        bpy.ops.object.select_all(action='SELECT')
        for o in context.selected_editable_objects:
            if o.scale[0] < 1.0:
                o.scale = (1.0, 1.0, 1.0)
            else:
                o.scale = (0.5, 0.5, 0.5)
        
        return {'FINISHED'}

############### GameOperator #################
class GameOperator(bpy.types.Operator):
    """ call GameOperator ID 
        - new Game - 3D Sudoku -
    """
    bl_idname = "wm.sudocubegame"
    bl_label = "New Game"
    bl_options = { "REGISTER", "UNDO", "PRESET" } 

    def execute(self, context):
        self.report({'INFO'}, "execute GameOperator")
        return {'FINISHED'} 

    def invoke(self, context, event):
        co = cm = cs = 0
        collection_name = "Collection"
        collection = bpy.data.collections[collection_name]
        bpy.ops.object.mode_set(mode='OBJECT')
        meshes = set()

        for obj in [o for o in collection.objects if o.type == 'MESH']:
            obj.active_material_index = 0
            for i in range(len(obj.material_slots)):
                bpy.ops.object.material_slot_remove({'object': obj})
                cs+=1         
            meshes.add( obj.data )
            bpy.data.objects.remove( obj )
            co+=1
        for mesh in [m for m in meshes if m.users == 0]:
            bpy.data.meshes.remove( mesh )
            cm+=1
             
        self.report({'INFO'}, "deleted - objects: %d meshes: %d material_slots: %d" % (co, cm, cs))
        
        bpy.ops.mesh.primitive_cube_add(enter_editmode=False, 
                        align='WORLD', 
                        calc_uvs=True, 
                        location=(0, 20, 0), 
                        scale=(.001, .001, .001))
        bpy.context.active_object.name  = '000-dummycube'
        bpy.context.active_object.data.name = '000-dummycube'

        for i in range(10):
            # script:   img = os.path.join(context.scene.sudocube_path.path, "images/%s.png" % (i))
            # add-on:
            img = os.path.join(context.preferences.addons[__name__].preferences.filepath, "%s.png" % (i))
            if os.path.exists(img) == True:            
                textur = bpy.data.images.load(img) 
                if cs<2:
                    mat = bpy.data.materials.new(name=str(i))
                else:
                    mat = bpy.data.materials.get(str(i))                    
            else:
                self.report({'INFO'}, "Missing texture: %s" % (img))
                return {'CANCELLED'}                       
        
            if mat == None:
                self.report({'INFO'}, "minimal scene requirements missing")
                return {'CANCELLED'}
             
            mat.use_nodes = True
            tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            tex_node.image = textur
            principled_BSDF = mat.node_tree.nodes.get('Principled BSDF')
            mat.node_tree.links.new(tex_node.outputs[0], principled_BSDF.inputs[0])
        if cm==0:
            self.report({'INFO'}, "new materials: %d" % (i))
        sl =[[1, 6, 3, 4, 5, 2, 7, 8, 9, 9, 7, 8, 3, 1, 6, 5, 2, 4, 2, 4, 5, 8, 9, 7, 6, 3, 1], [8, 6, 3, 4, 5, 2, 7, 1, 9, 9, 7, 1, 3, 8, 6, 5, 2, 4, 2, 4, 5, 1, 9, 7, 6, 3, 8], [8, 6, 3, 5, 4, 2, 9, 1, 7, 7, 9, 1, 3, 8, 6, 4, 2, 5, 2, 5, 4, 1, 7, 9, 6, 3, 8]] 
        slist = sl[random.choice((0, 1, 2))]
        sindex = random.choice((0, 9, 18))
        ex = 4.0
        scale = 2.0
        ovector = mathutils.Vector((-2.0, -2.0, -2.0))
        pvector = (mathutils.Vector(((2.0, 2.0, 5.0))) + ovector) * ex        
        mat = bpy.data.materials.get("0")
        bpy.context.active_object.data.materials.clear()    
        bpy.context.active_object.data.materials.append(mat)
        bpy.context.active_object.hide_select = True
        dif = 0
        for i in range(len(slist) ):
            x = (i%3)+1         
            y = ((i//9)%9)+1    
            z = ((i%9)//3)+1    
            m = slist[(i+sindex) % len(slist)]

            name = '%s%s%s' % (int(x),int(y),int(z))
            pvector = (mathutils.Vector((float(x),float(y),float(z))) + ovector) * ex
            bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', calc_uvs=True, location=pvector, scale=(scale, scale, scale))
            bpy.context.active_object.name  = name
            bpy.context.active_object.data.name = name
            mat = bpy.data.materials.get(str(m))
            bpy.context.active_object.data.materials.append(mat)
            bpy.ops.object.mode_set(mode="EDIT")
            mesh = bpy.context.active_object.data
            bpy.ops.uv.cube_project(cube_size=scale*ex, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=False)
            bpy.ops.object.mode_set(mode="OBJECT")

            if len(bpy.context.scene.sudocube_data) < len(slist):
                SetTings = bpy.context.scene.sudocube_data.add()
                SetTings.mat = str(int(m))
                SetTings.name = name
                SetTings.position_vector = pvector
            else:
                bpy.data.scenes['Scene'].sudocube_data[name].mat = str(int(m))
            
            di = 4
            if random.randrange(1,di) == 1:
                dif += 1
                mat = bpy.data.materials.get("0")
                bpy.context.active_object.data.materials.clear()    
                bpy.context.active_object.data.materials.append(mat)
        
        scoreInit()
        GameID = len(bpy.context.scene.score_data)
        bpy.context.scene.score_data[GameID-1].difficulty = dif
        bpy.context.space_data.shading.type = 'MATERIAL'       
        bpy.ops.view3d.view_all(center=True)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.properties.score_operator()       
        self.report({'INFO'}, "Game-%d zu loesen: %d" % (GameID, dif))
        
        return self.execute(context)

bpy.utils.register_class(GameOperator)

############### ScoreOperator #################
class ScoreOperator(bpy.types.Operator):
    """Computing Score and Time
    called by UI and GameOperator
    running modal
    """
    bl_idname = "properties.score_operator"
    bl_label = "Score Properties Operator"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'
        
    def execute(self, context):
        wm = context.window_manager
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        obj = context.object
        GameID = len(bpy.context.scene.score_data)

        if event.type in {'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE', 'TIMER'}:
            if bpy.context.scene.score_data[GameID-1].progress == 135:                
                end = time.perf_counter()
                duration = end - bpy.context.scene.score_data[GameID-1].starttime
                bpy.context.scene.score_data[GameID-1].duration = duration
                bpy.context.scene.score_data[GameID-1].plusscore = int(1350 / duration * bpy.context.scene.score_data[GameID-1].difficulty)
                id = score_total = 0
                while id < len(bpy.context.scene.score_data):
                    if bpy.context.scene.score_data[id].progress > 134:
                        score_total += bpy.context.scene.score_data[id].plusscore
                    id += 1
                bpy.context.scene.score_data[GameID-1].score_total = score_total

                if event.value in { 'CLICK', 'NOTHING', 'PRESS', 'RELEASE'}:
                    return {'FINISHED'}
                
                return {'PASS_THROUGH'}

            if context.active_object.type == 'MESH' and len(context.active_object.name) == 3:
                rem = progress = 0                
                if len(bpy.context.scene.sudocube_data) > 0:
                    for o in context.selectable_objects:
                        if (o.type == 'MESH') and (len(o.name) == 3):
                            if (int(o.active_material.name) >0) and (o.active_material.name == bpy.data.scenes['Scene'].sudocube_data[o.name].mat):
                                progress += int(o.active_material.name)
                            elif (int(o.active_material.name) >0) and (o.active_material.name != bpy.data.scenes['Scene'].sudocube_data[o.name].mat):
                                progress -= int(o.active_material.name)
                                rem += 1
                            elif (int(o.active_material.name) == 0):
                                rem += 1
                    bpy.context.scene.score_data[GameID-1].progress = progress
                    bpy.context.scene.score_data[GameID-1].plusscore = progress
                    colorpercent = progress/135
                    color = bpy.context.preferences.themes[0].view_3d.space.gradients.high_gradient
                    color.s = 1.0
                    color.h = colorpercent
                
                end = time.perf_counter()
                duration = end - bpy.context.scene.score_data[GameID-1].starttime
                bpy.context.scene.score_data[GameID-1].duration = duration
                if duration > 0:
                    score_int = str(int(bpy.context.scene.score_data[GameID-1].plusscore / duration * 10 * bpy.context.scene.score_data[GameID-1].difficulty))
                else:
                    score_int = str(int(bpy.context.scene.score_data[GameID-1].plusscore * 10 * bpy.context.scene.score_data[GameID-1].difficulty))

            return {'PASS_THROUGH'}
    
        return {"PASS_THROUGH"}

############### SudoCubeSettings #################
class SudoCubeSettings(bpy.types.PropertyGroup):
    mat: bpy.props.StringProperty(name="SudoCube Material Property", default='0')
    name: bpy.props.StringProperty(name="SudoCube Key Property", default='000-dummycube')
    position_vector: bpy.props.FloatVectorProperty(name="SudoCube Position Property", default=(0,0,0))

bpy.utils.register_class(SudoCubeSettings)
bpy.types.Scene.sudocube_data = bpy.props.CollectionProperty(type=SudoCubeSettings)

############### SudoCubeScore #################
class SudoCubeScore(bpy.types.PropertyGroup):
    progress: bpy.props.IntProperty()
    plusscore: bpy.props.IntProperty()
    duration: bpy.props.FloatProperty()
    starttime: bpy.props.FloatProperty()
    difficulty: bpy.props.IntProperty()
    game: bpy.props.IntProperty()
    score_total: bpy.props.IntProperty()

bpy.utils.register_class(SudoCubeScore)

bpy.types.Scene.score_data = bpy.props.CollectionProperty(type=SudoCubeScore)

def scoreInit():
    Score = bpy.context.scene.score_data.add()
    Score.starttime = time.perf_counter()
    Score.progress = 0
    Score.plusscore = 0
    Score.duration = 0
    Score.difficulty = 0
    Score.game = len(bpy.context.scene.score_data)
    Score.score_total = 0

############### Addon Preferences ###############
class SudocubeAddonPreferences(AddonPreferences):
    """Sudocube Texture preferences"""
    bl_idname = __name__

    filepath: StringProperty(
        name="Texture Filepath",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Texture folder (images) for Sudocube Add-on")
        layout.prop(self, "filepath")

############### Preferences Operator ###############
class OBJECT_OT_addon_sudocube_prefs(Operator):
    """Display Sudocube preferences"""
    bl_idname = "object.addon_sudocube_prefs"
    bl_label = "Add-on Sudocube Prefs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        info = ("Path: %s" % addon_prefs.filepath)

        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(PathPanel)
    bpy.utils.register_class(SudoCubePanel)
    bpy.utils.register_class(ExplodeOperator) 
    bpy.utils.register_class(ScoreOperator)
    bpy.utils.register_class(OBJECT_OT_addon_sudocube_prefs)
    bpy.utils.register_class(SudocubeAddonPreferences)

def unregister():
    bpy.utils.unregister_class(PathPanel)
    bpy.utils.unregister_class(SudoCubePanel)
    bpy.utils.unregister_class(ExplodeOperator) 
    bpy.utils.unregister_class(GameOperator)
    bpy.utils.unregister_class(ScoreOperator)
    bpy.utils.unregister_class(OBJECT_OT_addon_sudocube_prefs)
    bpy.utils.unregister_class(SudocubeAddonPreferences)


if __name__ == "__main__":
    register()
