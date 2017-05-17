import bpy
import walls
import joinery

class createWallOperator(bpy.types.Operator):
    bl_idname = "architect.create_wall_operator"
    bl_label = "Wall Operator"
    bl_description = "Create Wall"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wall = walls.CWall()
        wall.components.add(height=2.81,thickness=0.10,color=0)
        wall.sections.add(3,0)
        wall.update()
        
        context.window_manager.wallProperties.changed = True
        return {"FINISHED"}
    
class addWallSectionOperator(bpy.types.Operator):
    bl_idname = "architect.add_wall_section_operator"
    bl_label = "Add Wall Section Operator"
    bl_description = "Add Wall Section"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        current_object = context.object
        if current_object == None:
            return
        
        wall = context.window_manager.elements.findByObject(current_object)  
        
        if wall.sections.count() > 0:
            length = wall.sections.last().length
            angle = (wall.sections.last().angle + 270)%360
        else:
            length = 3
            angle = 0
        wall.sections.add(length,angle)
        wall.update()
        
        context.window_manager.wallProperties.changed = True
        return {"FINISHED"}
    
class removeWallSectionOperator(bpy.types.Operator):
    bl_idname = "architect.remove_wall_section_operator"
    bl_label = "Add Wall Component Operator"
    bl_description = "Add Wall Component"
    bl_options = {"REGISTER"}
    
    index = bpy.props.IntProperty(name="section index", default=-1)
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        current_object = context.object
        if current_object == None:
            return
        
        wall = context.window_manager.elements.findByObject(current_object)  
        if wall.sections.count() == 0:
            return
        wall.sections.delete(self.index)
        wall.update()
        
        context.window_manager.wallProperties.changed = True
        return {"FINISHED"}

class addWallComponentOperator(bpy.types.Operator):
    bl_idname = "architect.add_wall_component_operator"
    bl_label = "Add Wall Component Operator"
    bl_description = "Add Wall Component"
    bl_options = {"REGISTER"}
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        current_object = context.object
        if current_object == None:
            return
        
        wall = context.window_manager.elements.findByObject(current_object)  
        
        if wall.components.count() > 0:
            height = wall.components.last().height
            thickness = wall.components.last().thickness
            color = wall.components.last().color
        else:
            height=2.81
            thickness=0.10
            color=0
        wall.components.add(height=height,thickness=thickness,color=color)
        wall.update()
        
        context.window_manager.wallProperties.changed = True
        return {"FINISHED"}

class removeWallComponentOperator(bpy.types.Operator):
    bl_idname = "architect.remove_wall_component_operator"
    bl_label = "Add Wall Component Operator"
    bl_description = "Add Wall Component"
    bl_options = {"REGISTER"}
    
    index = bpy.props.IntProperty(name="component index", default=-1)
    
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        current_object = context.object
        if current_object == None:
            return
        
        wall = context.window_manager.elements.findByObject(current_object)  
           
        if wall.components.count() == 0:
            return
        print('removing component #', self.index)
        wall.components.delete(self.index)
        wall.update()
        
        context.window_manager.wallProperties.changed = True
        return {"FINISHED"}

############################################################################

class createWindowOperator(bpy.types.Operator):
    bl_idname = "architect.create_window_operator"
    bl_label = "Window Operator"
    bl_description = "Create Window"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        window = joinery.CWindow()
        window.width = 2.0
        window.height = 1.5
        window.frame.thickness = 0.08
        window.frame.divisions.direction = 'HORIZONTAL'
        window.frame.insertPane()
        window.update()
        window.select()
        return {"FINISHED"}
    
