import bpy

class DatasetFromCameras_UI(bpy.types.Panel):
    '''Dataset From Cameras UI'''
    bl_idname = 'panel.dataset_from_cameras_ui'
    bl_label = 'Dataset From Cameras DFC'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderNeRF'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.alignment = 'CENTER'

        layout.use_property_split = True
        layout.prop(scene, 'train_camera_collection')
        layout.prop(scene, 'test_camera_collection')

        layout.separator()
        layout.prop(scene, 'dfc_dataset_name')

        layout.separator()
        layout.operator('object.dataset_from_cameras', text='PLAY DFC')