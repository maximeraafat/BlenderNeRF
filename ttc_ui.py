import bpy


# train and test cameras ui class
class TTC_UI(bpy.types.Panel):
    '''Train and Test Cameras UI'''
    bl_idname = 'VIEW3D_PT_ttc_ui'
    bl_label = 'Train and Test Cameras TTC'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlenderNeRF'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.alignment = 'CENTER'

        layout.use_property_split = True
        layout.prop(scene, 'ttc_nb_frames')
        layout.prop_search(scene, 'camera_train_target', scene, 'objects')
        layout.prop_search(scene, 'camera_test_target', scene, 'objects')

        layout.separator()
        layout.prop(scene, 'ttc_dataset_name')

        layout.separator()
        layout.operator('object.train_test_cameras', text='PLAY TTC')