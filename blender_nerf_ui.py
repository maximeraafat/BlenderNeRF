import bpy


# blender nerf shared ui properties class
class BlenderNeRF_UI(bpy.types.Panel):
    '''BlenderNeRF UI'''
    bl_idname = 'panel.blender_nerf_ui'
    bl_label = 'BlenderNeRF shared UI'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderNeRF'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.alignment = 'CENTER'
        row = layout.row(align=True)

        row.prop(scene, 'train_data', toggle=True)
        row.prop(scene, 'test_data', toggle=True)

        if not (scene.train_data or scene.test_data):
            layout.label(text='Nothing will happen!')

        else:
            layout.prop(scene, 'aabb')

            if scene.train_data:
                layout.separator()
                layout.prop(scene, 'render_frames')

            layout.separator()
            layout.use_property_split = True
            layout.prop(scene, 'save_path')