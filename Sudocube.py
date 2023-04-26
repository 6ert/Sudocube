#######################################################################################
## Title: Sudocube
## Author: Gert Weber • info@weberlebt.de • https://weberlebt.de • 2023
## License: CC BY lizenz • Namensnennung 2.0 Deutschland (CC BY 2.0 DE) • https://creativecommons.org/licenses/by/2.0/de/legalcode
## Blender: Blender is released under the GNU General Public License • http://download.blender.org/release/GPL-license.txt
## Disclaimer: The author makes no representations or warranties about the non-infringement or absence of other defects concerning the CC-licensed work.
#######################################################################################
## Add-on Mode:
# bl_info = {
#     "name": "Sudocube",
#     "blender": (3, 3, 1),
#     "category": "Object",
# }
# import time
# print("Sleeping 3 before importing")
# time.sleep(3)

import bpy
import sys
import mathutils
import random
import time
import os
# from bpy.app.handlers import persistent
# blend_dir = os.path.dirname(bpy.data.filepath)
# if blend_dir not in sys.path:
#     sys.path.append(blend_dir)
# import Sudocube
# import importlib
# importlib.reload(Sudocube)
# Sudocube.main()

############### PathPanel #################
class PathPanel(bpy.types.Panel):
    """Creates FilePath Panel in View-3D - Sidebar(shortcut: N) - Sudocube"""
    bl_idname = "OBJECT_PT_pathpanel"
    bl_label = "Path"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Sudocube"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Path to images folder")
       
        col = layout.column(align=True)
        col.prop(context.scene.sudocube_path, "path")

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
        
        if context.scene.sudocube_path.path == "":
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
            img = os.path.join(context.scene.sudocube_path.path, "images/%s.png" % (i))
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

############### SudocubeSystemProperties #################
class SudocubeSystemProperties(bpy.types.PropertyGroup):
    """ bpy.data.filepath
    not available in Add-on Mode!
    Run in Scripting Mode """
    # bl_idname = "scene.init_my_prop"
    # bl_label = "Init my_prop"

    path : bpy.props.StringProperty(
        name="",
        description="Path to Directory",
        default=os.path.dirname(bpy.data.filepath), # AttributeError 'RestrictData' object has no attribute 'filepath'
        # if you see an exception like this, then the addon needs to be updated to access the context during execution rather then on registration
        # default=os.path.dirname(__file__), # Addon: Missing texture: C:\Users\root\AppData\Roaming\Blender Foundation\Blender\3.3\scripts\addons\images/0.png
        # default=os.getcwd(), # C:\Program Files\blender-3.3.1
        # default=sys.argv[0], # C:\Program Files\blender-3.3.1
        # (type alias) path: Module("os.path")
        # OS routines for NT or Posix depending on what system we're on.
        # This exports:
        # all functions from posix or nt, e.g. unlink, stat, etc.
        # os.path is either posixpath or ntpath
        # os.name is either 'posix' or 'nt'
        # os.curdir is a string representing the current directory (always '.')
        # os.pardir is a string representing the parent directory (always '..')
        # os.sep is the (or a most common) pathname separator ('/' or '\')
        # os.extsep is the extension separator (always '.')
        # os.altsep is the alternate pathname separator (None or '/')
        # os.pathsep is the component separator used in $PATH etc
        # os.linesep is the line separator in text files ('\r' or '\n' or '\r\n')
        # os.defpath is the default search path for executables
        # os.devnull is the file path of the null device ('/dev/null', etc.)
        # Programs that import and use 'os' stand a better chance of being portable between different platforms. 
        # Of course, they must then only use functions that are defined by all platforms (e.g., unlink and opendir), 
        # and leave all pathname manipulation to os.path (e.g., split and join)
        maxlen=1024,
        subtype='DIR_PATH'
        )

    # @classmethod
    # @bpy.app.handlers.persistent
    # def poll(cls, context):
    #     # return context.active_object is not None
    #     return cls.path is not None
 
    # def execute(self, context):
    #     if context.scene.my_prop != "initialized":
    #         context.scene.my_prop = "initialized"
    #         self.__class__.bl_label = "Change my_prop"
    #     else:
    #         context.scene.my_prop = "foobar"
    #         self.__class__.bl_label = self.bl_label
    #     return {'FINISHED'}
        
bpy.utils.register_class(SudocubeSystemProperties)
bpy.types.Scene.sudocube_path = bpy.props.PointerProperty(type=SudocubeSystemProperties)
# bpy.types.Scene.sudocube_path: bpy.props.PointerProperty(type=SudocubeSystemProperties) # # can't access bpy.context here!
# bpy.app.handlers.save_post.append(bpy.types.Scene.sudocube_path)

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

def register():
    # bpy.types.Scene.sudocube_path = bpy.props.PointerProperty(type=SudocubeSystemProperties) # # can't access bpy.context here!
    # bpy.app.handlers.save_post.append(bpy.types.Scene.sudocube_path)
    bpy.utils.register_class(PathPanel)
    bpy.utils.register_class(SudoCubePanel)
    bpy.utils.register_class(ExplodeOperator) 
    bpy.utils.register_class(ScoreOperator)

def unregister():
    bpy.utils.unregister_class(SudocubeSystemProperties)
    bpy.utils.unregister_class(PathPanel)
    bpy.utils.unregister_class(SudoCubePanel)
    bpy.utils.unregister_class(ExplodeOperator) 
    bpy.utils.unregister_class(GameOperator)
    bpy.utils.unregister_class(ScoreOperator)

# call in Add-on Mode:
# if __name__ == "__main__":
register()
