import os
import shutil
import bpy
from . import blender_nerf_operator


# global addon script variables
OUTPUT_TRAIN = 'images_train'
TRAIN_CAM = 'Train Cam'
TEST_CAM = 'Test Cam'


# train and test cameras operator class
class TrainTestCameras(blender_nerf_operator.BlenderNeRF_Operator):
    '''Train and Test Cameras Operator'''
    bl_idname = 'object.train_test_cameras'
    bl_label = 'Train and Test Cameras TTC'

    def execute(self, context):
        scene = context.scene
        train_camera = scene.camera_train_target
        test_camera = scene.camera_test_target

        # check if cameras are selected : next errors depend on existing cameras
        if train_camera == None or test_camera == None:
            self.report({'ERROR'}, 'Be sure to have selected a train and test camera!')
            return {'FINISHED'}

        # if there is an error, print first error message
        error_messages = self.asserts(scene, method='TTC')
        if len(error_messages) > 0:
           self.report({'ERROR'}, error_messages[0])
           return {'FINISHED'}

        output_train_data = self.get_camera_intrinsics(scene, train_camera)
        output_test_data = self.get_camera_intrinsics(scene, test_camera)

        # clean directory name (unsupported characters replaced) and output path
        output_dir = bpy.path.clean_name(scene.ttc_dataset_name)
        output_path = os.path.join(scene.save_path, output_dir)

        # initial property values might have changed since depsgraph_update_post handler
        scene.init_frame_step = scene.frame_step # not needed, but simplifies post_render handler function
        scene.init_output_path = scene.render.filepath

        if scene.test_data:
            output_test_path = os.path.join(output_path, '%s_test' % output_dir)
            os.makedirs(output_test_path, exist_ok=True)

            # testing transforms
            output_test_data['frames'] = self.get_camera_extrinsics(scene, test_camera, mode='TEST', method='TTC')
            self.save_json(output_test_path, 'transforms_test.json', output_test_data)

        if scene.train_data:
            output_train_path = os.path.join(output_path, '%s_train' % output_dir)
            output_train = os.path.join(output_train_path, OUTPUT_TRAIN)
            os.makedirs(output_train, exist_ok=True)

            # training transforms
            output_train_data['frames'] = self.get_camera_extrinsics(scene, train_camera, mode='TRAIN', method='TTC')
            self.save_json(output_train_path, 'transforms_train.json', output_train_data)

            if scene.render_frames:
                scene.is_rendering = (False, True, False)
                scene.render.filepath = os.path.join(output_train, '') # training frames path
                bpy.ops.render.render(scene='INVOKE_DEFAULT', animation=True, write_still=True) # render scene

        # if frames are rendered, the below code is executed by the handler function
        if not any(scene.is_rendering):
            # compress dataset and remove folder (only keep zip)
            shutil.make_archive(output_path, 'zip', output_path) # output filename = output_path
            shutil.rmtree(output_path)

        return {'FINISHED'}
