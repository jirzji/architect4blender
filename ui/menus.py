import bpy

class view3DMenu(bpy.types.Menu):
    bl_idname = "view3d.architect_menu"
    bl_label = "Architect"
    bl_space_type = "VIEW_3D"

    def draw(self, context):
        layout = self.layout
        layout.operator("architect.create_wall_operator", "Wall")
        layout.operator("architect.create_window_operator", "Window")
        
