import bpy

class COS_UI(bpy.types.Panel):
    '''Camera Oriented Sampling UI'''
    bl_idname = 'panel.cos_ui'
    bl_label = 'Camera Oriented Sampling COS'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderNeRF'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.alignment = 'CENTER'

        layout.use_property_split = True
        layout.prop_search(scene, 'camera_target', scene, 'objects')

        layout.separator()
        layout.prop(scene, 'cos_radius')
        layout.use_property_split = True
        layout.prop(scene, 'cos_train_num_samples')
        layout.prop(scene, 'cos_test_num_samples')
        layout.prop(scene, 'cos_above_horizon_only')

        layout.separator()
        layout.operator('object.random_cameras_around_origin', text='create collection of random cameras')