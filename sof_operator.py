import os
import shutil
import bpy
from . import blender_nerf_operator


# global addon script variables
OUTPUT_TRAIN = 'images_train'


# subset of frames operator class
class SubsetOfFrames(blender_nerf_operator.BlenderNeRF_Operator):
    '''Subset of Frames Operator'''
    bl_idname = 'object.subset_of_frames'
    bl_label = 'Subset of Frames SOF'

    def execute(self, context):
        scene = context.scene
        camera = scene.camera

        # check if camera is selected : next errors depend on an existing camera
        if camera == None:
            self.report({'ERROR'}, 'Be sure to have a selected camera!')
            return {'FINISHED'}

        # if there is an error, print first error message
        error_messages = self.asserts(scene, method='SOF')
        if len(error_messages) > 0:
           self.report({'ERROR'}, error_messages[0])
           return {'FINISHED'}

        output_data = self.get_camera_intrinsics(scene, camera)

        # clean directory name (unsupported characters replaced) and output path
        output_dir = bpy.path.clean_name(scene.sof_dataset_name)
        output_path = os.path.join(scene.save_path, output_dir)

        # initial property values might have changed since depsgraph_update_post handler
        scene.init_frame_step = scene.frame_step
        scene.init_output_path = scene.render.filepath

        if scene.test_data:
            output_test_path = os.path.join(output_path, '%s_test' % output_dir)
            os.makedirs(output_test_path, exist_ok=True)

            # testing transforms
            output_data['frames'] = self.get_camera_extrinsics(scene, camera, mode='TEST', method='SOF')
            self.save_json(output_test_path, 'transforms_test.json', output_data)

        if scene.train_data:
            output_train_path = os.path.join(output_path, '%s_train' % output_dir)
            output_train = os.path.join(output_train_path, OUTPUT_TRAIN)
            os.makedirs(output_train, exist_ok=True)

            # training transforms
            output_data['frames'] = self.get_camera_extrinsics(scene, camera, mode='TRAIN', method='SOF')
            self.save_json(output_train_path, 'transforms_train.json', output_data)

            if scene.render_frames:
                scene.is_rendering = (True, False, False)
                scene.frame_step = scene.train_frame_steps # update frame step
                scene.render.filepath = os.path.join(output_train, '') # training frames path
                bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True) # render scene

        # if frames are rendered, the below code is executed by the handler function
        if not any(scene.is_rendering):
            # compress dataset and remove folder (only keep zip)
            shutil.make_archive(output_path, 'zip', output_path) # output filename = output_path
            shutil.rmtree(output_path)

        return {'FINISHED'}
