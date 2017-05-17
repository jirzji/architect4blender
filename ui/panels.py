import bpy
import os
import walls
import joinery
                
class ToolPanel(bpy.types.Panel):
    bl_idname = "view3d.tool_panel"
    bl_label = "Architect"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Architect"

    def draw(self, context):
        layout = self.layout
        layout.operator("architect.create_wall_operator", "Wall") 
        layout.operator("architect.create_window_operator", "Window") 
        
#########################################################################################

def update_wall(self, context):
    if (context.area.type!="VIEW_3D") or (context.region.type != "UI"):
        return
    
    if context.object == None:
        return
    
    props = context.window_manager.wallProperties
    if props.syncing:
        return
    
    props.changed = True
    wall = context.window_manager.elements.findByObject(context.object)
    if wall == None:
        return

    wall.components.clear()
    for component in props.components:
        wall.components.add(component.height, component.thickness, component.reveal, component.elevation, component.type, component.color)
    wall.sections.clear()
    for section in props.sections:
        wall.sections.add(section.length, section.angle, section.inclination)        
    wall.close = props.close
 
    print("wall update")
    print("wall=, wall")
    wall.update()

class WallComponentProperty(bpy.types.PropertyGroup):
    type = bpy.props.EnumProperty(name='Type', description='Wall Component Type', items = (('WALL', 'WALL', 'Wall Skin Component'), ('CAVITY', 'CAVITY', 'Wall Cavity Component')), update=update_wall)
    reveal = bpy.props.FloatProperty(name='Reveal', min=0.0, max=1.0, default=0, precision=3, description='Wall Component Reveal', update=update_wall)
    elevation = bpy.props.FloatProperty(name='Elevation', min=0.00, max=1.00, default=0, precision=3, description='Wall Component Elevation', update=update_wall)
    height = bpy.props.FloatProperty(name='Height', default=2.81, precision=3, description='Wall Component Height', update=update_wall)
    thickness = bpy.props.FloatProperty(name='Thickness', min=0.00, max=1.00, default=0, precision=3, description='Wall Component Thickness', update=update_wall)
    color = bpy.props.IntProperty(name='Color', default=0, description='Wall Component Color', update=update_wall)

class WallSectionProperty(bpy.types.PropertyGroup):
    length = bpy.props.FloatProperty(name='Length', min=0.1, max=1000, default=3, precision=3, description='Wall Section Length', update=update_wall)
    angle = bpy.props.FloatProperty(name='Angle', min=0.00, max=360, default=0, precision=3, description='Wall Section Angle', update=update_wall)
    inclination = bpy.props.FloatProperty(name='Inclination', min=-1.0, max=1.0, default=0, precision=3, description='Wall Section Inclination', update=update_wall)
  
class WallProperties(bpy.types.PropertyGroup):
    changed = bpy.props.BoolProperty(default=True)
    syncing = bpy.props.BoolProperty(default=False)
    components = bpy.props.CollectionProperty(type=WallComponentProperty)        
    sections = bpy.props.CollectionProperty(type=WallSectionProperty) 
    close = bpy.props.BoolProperty(name='Close', default=False, description='Wall Closing', update=update_wall)       
        
class WallPropertiesPanel(bpy.types.Panel):
    bl_idname = "view3d.wall_properties_panel"
    bl_label = "Wall Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Architect"
    
    #element = None
            
    def setUIProperties(context, wall):
        print("WallPropertiesPanel.setUIProperties")
        props = context.window_manager.wallProperties
        if not props.changed:
            return props
        props.syncing = True
        props.components.clear()
        for item in wall.components:
            print("add prop component")
            componentProperty = props.components.add()
            componentProperty.type = item.type
            componentProperty.reveal = item.reveal
            componentProperty.elevation = item.elevation
            componentProperty.height = item.height         
            componentProperty.thickness = item.thickness
            componentProperty.color = item.color  
        props.sections.clear()
        for item in wall.sections:
            print("add prop section")
            sectionProperty = props.sections.add()
            sectionProperty.length = item.length
            sectionProperty.angle = item.angle
            sectionProperty.inclination = item.inclination  
        props.close = wall.close
        props.syncing = False
        props.changed = False
        return props
    
    @classmethod
    def poll(self, context):
        print("*** WallPropertiesPanel.poll")
        if context.object is None:
            return False        
        if not context.object.select:
            return False
        wall = context.window_manager.elements.findByObject(context.object)
        if wall == None:
            return
        if type(wall) is not walls.CWall:
            return False
        self.setUIProperties(context, wall)
        return True

    def invoke(self, context):
        print("** WallPropertiesPanel.invoke")
        
    def draw(self, context):
        print("*** WallPropertiesPanel.draw")
        props = context.window_manager.wallProperties
            
        layout = self.layout
        layout.prop(props, "close")
        row = layout.row()
        row.label("Components:")
        row.operator("architect.add_wall_component_operator", "+") 
        for index, component in enumerate(props.components):
            box = layout.box()
            row = box.row()
            row.label("component #"+str(index))
            row.operator("architect.remove_wall_component_operator", "-").index = index
            col = box.column(align=True)
            col.prop(component, "type")
            if component.type == "WALL":
                col.prop(component, "reveal")
                col.prop(component, "elevation")
                col.prop(component, "height")
                col.prop(component, "thickness")
                col.prop(component, "color")
            
        row = layout.row()
        row.label("Sections:")
        row.operator("architect.add_wall_section_operator", "+") 
        for index, section in enumerate(props.sections):
            box = layout.box()
            row = box.row()
            row.label("section #"+str(index))
            row.operator("architect.remove_wall_section_operator", "-").index = index
            col = box.column(align=True)
            col.prop(section, "length")
            col.prop(section, "angle")
            col.prop(section, "inclination")
            
##################################################################################
        
repo = {}

def update_window(self, context):
    print("&&& update_window")
    if (context.area.type!="VIEW_3D") or (context.region.type != "UI"):
        return
    
    if context.object == None:
        return
    
    props = context.window_manager.windowProperties
    if props.syncing:
        print("props syncing")
        return
    
    props.changed = True
    window = context.window_manager.elements.findByObject(context.object)
    if window == None:
        return

    print("window update")
    window.height = props.height
    window.width = props.width
    print("props.wallInfo.wall=",props.wallInfo.wall)
    if props.wallInfo.wall != "-":
        wall = context.window_manager.elements.findByname(props.wallInfo.wall)
        # TODO parameters
        print("insert in wall", wall)
        posInWall = (props.wallInfo.distance,props.wallInfo.base)
        window.insertInWall(wall, sectionIndex = 0, componentIndex = 0, position = (0,0))
 
    window.update()
        
class WallPositionProperty(bpy.types.PropertyGroup):
    distance = bpy.props.FloatProperty(update=update_window)
    base = bpy.props.FloatProperty(update=update_window)

def enum_walls(self, context):
    print("enum_walls callback")
    enum_items = [("-", "-", "")]
    wall_list = context.window_manager.elements.listOfType(walls.CWall)
    for index, element in enumerate(wall_list):
        enum_items.append((element.name, element.name, ""))
    print(enum_items)
    return enum_items

class WallInfoProperty(bpy.types.PropertyGroup):
    wall = bpy.props.EnumProperty(items = enum_walls, update=update_window)
    component = bpy.props.IntProperty(update=update_window)
    section = bpy.props.IntProperty(update=update_window)
#    position = bpy.props.PointerProperty(type=WallPositionProperty)
    distance = bpy.props.FloatProperty(update=update_window)
    base = bpy.props.FloatProperty(update=update_window)

class JoineryProperties(bpy.types.PropertyGroup):
    syncing = bpy.props.BoolProperty(default=False)
    height = bpy.props.FloatProperty(precision=3,update=update_window)
    width = bpy.props.FloatProperty(precision=3,update=update_window)
    wallInfo = bpy.props.PointerProperty(type=WallInfoProperty)

def enum_previews(path):
    enum_items = []

    directory = os.path.join(os.path.dirname(__file__), path)      

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        file_names = os.listdir(directory)
        if len(file_names) == 0:
            return enum_items
        print("Scanning directory: %s" % directory)
        image_paths = []
        for fn in file_names:
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            thumb = repo['window'].load(filepath, filepath, 'IMAGE')
            enum_items.append((os.path.splitext(name)[0], os.path.splitext(name)[0], "", thumb.icon_id, i))

    return enum_items
    
def enum_window_types(self, context):
    print("enum_window_types callback")

#    if context is None:
#        return []

    if repo['window'].types != []:
        return repo['window'].types

    repo['window'].types = enum_previews('img/windows/types')
    return repo['window'].types

def enum_window_shapes(self, context):
    print("enum_window_shapes callback")

#    if context is None:
#        return []

    if repo['window'].shapes != []:
        return repo['window'].shapes

    repo['window'].shapes = enum_previews('img/windows/shapes')
    return repo['window'].shapes

class WindowProperties(bpy.types.PropertyGroup):
    changed = bpy.props.BoolProperty(default=True)
    syncing = bpy.props.BoolProperty(default=False)
    height = bpy.props.FloatProperty(precision=3,update=update_window)
    width = bpy.props.FloatProperty(precision=3,update=update_window)
    type = bpy.props.EnumProperty(items = enum_window_types, update=update_window)
    shape = bpy.props.EnumProperty(items = enum_window_shapes, update=update_window)
    wallInfo = bpy.props.PointerProperty(type=WallInfoProperty)

class WindowPropertiesPanel(bpy.types.Panel):
    bl_idname = "view3d.window_properties_panel"
    bl_label = "Window Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Architect"
    
    def setUIProperties(context, window):
        print("WindowPropertiesPanel.setUIProperties")
        props = context.window_manager.windowProperties
        if not props.changed:
            return props
        props.syncing = True
        props.width = window.width
        props.height = window.height
        if window.wallInfo != None:
            props.wallInfo.wall = window.wallInfo.wall.name
            props.wallInfo.component = window.wallInfo.componentIndex
        else:
            props.wallInfo.wall = "-"
            props.wallInfo.component = 0
        print("wallInfo.wall=", props.wallInfo.wall)
        props.syncing = False
        props.changed = False
        return props
    
    def getProperties(self, windowObject):
        return self.properties
    
    @classmethod
    def poll(self, context):
        print("*** WindowPropertiesPanel.poll")
        if context.object is None:
            return False        
        if not context.object.select:
            return False
        window = context.window_manager.elements.findByObject(context.object)
        if window == None:
            return False
        if type(window) is not joinery.CWindow:
            return False
        self.setUIProperties(context, window)
        return True

    def draw(self, context):
        print("*** WindowPropertiesPanel.draw")
        props = context.window_manager.windowProperties
        
        layout = self.layout

        layout.prop(props, "height")
        layout.prop(props, "width")
        layout.template_icon_view(props, "type")
        layout.template_icon_view(props, "shape")
        props = props.wallInfo
        layout.prop(props, "wall")
        if props.wall != "-":
            layout.prop(props, "distance")
            layout.prop(props, "base")

#############################################################################
def setup():

    import bpy.utils.previews
    repo['window'] = bpy.utils.previews.new()
    repo['window'].types = []
    repo['window'].shapes = []
    
    #single variable as work buffer
    bpy.types.WindowManager.wallProperties = bpy.props.PointerProperty(type=WallProperties)
    bpy.types.WindowManager.windowProperties = bpy.props.PointerProperty(type=WindowProperties)  
    
def teardown():
    bpy.utils.previews.remove(repo['window'])    
    repo.clear()
      
if __name__ == '__main__':
    setup()
    teardown()