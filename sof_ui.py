import bpy


# subset of frames ui class
class SOF_UI(bpy.types.Panel):
    '''Subset of Frames UI'''
    bl_idname = 'VIEW3D_PT_sof_ui'
    bl_label = 'Subset of Frames SOF'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderNeRF'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.alignment = 'CENTER'

        layout.prop(scene, 'train_frame_steps')

        layout.use_property_split = True
        layout.prop(scene, 'camera')

        layout.separator()
        layout.prop(scene, 'sof_dataset_name')

        layout.separator()
        layout.operator('object.subset_of_frames', text='PLAY SOF')