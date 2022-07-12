import bpy


# subset of frames ui class
class SOF_UI(bpy.types.Panel):
    '''Subset of Frames UI'''
    bl_idname = 'panel.sof_ui'
    bl_label = 'Subset of frames SOF'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blender x NeRF'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # layout.use_property_split = True
        layout.alignment = 'CENTER'

        row = layout.row()

        row.prop(scene, 'train_data', toggle=True)
        row.prop(scene, 'test_data', toggle=True)

        layout.prop(scene, 'camera')
        layout.prop(scene, 'aabb')
        layout.prop(scene, 'train_frame_steps')
        layout.prop(scene, 'render_frames')
        layout.prop(scene, 'save_path')
        layout.prop(scene, 'dataset_name')

        layout.use_property_split = True
        layout.operator('object.subset_of_frames', text='PLAY SOF')
