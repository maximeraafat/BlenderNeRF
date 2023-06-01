import os
import shutil
import time

import bpy
from . import blender_nerf_operator


# global addon script variables
OUTPUT_TRAIN = 'images_train'
OUTPUT_TEST = 'images_test'

class DatasetFromCameras(blender_nerf_operator.BlenderNeRF_Operator):
    """
    Blender x NeRF Dataset From Cameras Operator, creates a dataset by running all the frames of all the cameras in the scene.
    """
    bl_idname = 'object.dataset_from_cameras'
    bl_label = 'Dataset From Cameras'

    def execute(self, context):
        scene = context.scene


        error_messages = self.asserts(scene, method='DFC')
        if len(error_messages) > 0:
           self.report({'ERROR'}, error_messages[0])
           return {'FINISHED'}

        # clean directory name (unsupported characters replaced) and output path
        output_dir = bpy.path.clean_name(scene.dfc_dataset_name)
        output_path = os.path.join(scene.save_path, output_dir)

        # initial property values might have changed since depsgraph_update_post handler
        scene.init_frame_step = scene.frame_step
        scene.init_output_path = scene.render.filepath


        if scene.train_data and scene.train_camera_collection is not None:
            output_train_path = os.path.join(output_path, '%s_train' % output_dir)
            output_train = os.path.join(output_train_path, OUTPUT_TRAIN)
            os.makedirs(output_train, exist_ok=True)

            # training transforms
            first_camera = scene.train_camera_collection.objects[0]
            output_train_data = self.get_camera_intrinsics(scene, first_camera)
            output_train_data['frames'] = []
            for camera in scene.train_camera_collection.objects:
                output_train_data['frames'] += self.get_camera_extrinsics(scene, camera, mode='TRAIN', method='DFC')
                bpy.context.scene.camera = camera
                print("Rendering camera: " + camera.name)
                if scene.render_frames:
                    # scene.is_rendering = (False, True, False)
                    scene.render.filepath = os.path.join(output_train, camera.name) # training frames path
                    init_frame = scene.frame_current
                    bpy.ops.render.render(write_still=True) # render scene
                    scene.frame_set(init_frame) # reset frame
                    #time.sleep(0.01)


            self.save_json(output_train_path, 'transforms_train.json', output_train_data)
            scene.frame_step = scene.init_frame_step
            scene.render.filepath = scene.init_output_path

        if scene.test_data and scene.test_camera_collection is not None:
            output_test_path = os.path.join(output_path, '%s_test' % output_dir)
            output_test = os.path.join(output_test_path, OUTPUT_TEST)
            os.makedirs(output_test, exist_ok=True)

            # testing transforms
            first_camera = scene.test_camera_collection.objects[0]
            output_test_data = self.get_camera_intrinsics(scene, first_camera)
            output_test_data['frames'] = []
            for camera in scene.test_camera_collection.objects:
                output_test_data['frames'] += self.get_camera_extrinsics(scene, camera, mode='TEST', method='DFC')
                bpy.context.scene.camera = camera
                print("Rendering camera: " + camera.name)
                if scene.render_frames:
                    # scene.is_rendering = (False, True, False)
                    scene.render.filepath = os.path.join(output_test, camera.name)
                    init_frame = scene.frame_current
                    bpy.ops.render.render(write_still=True)
                    scene.frame_set(init_frame)

            self.save_json(output_test_path, 'transforms_test.json', output_test_data)
            scene.frame_step = scene.init_frame_step
            scene.render.filepath = scene.init_output_path

        return {'FINISHED'}