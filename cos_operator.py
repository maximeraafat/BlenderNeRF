import os
import shutil
import bpy
from . import blender_nerf_operator


# global addon script variables
OUTPUT_TRAIN = 'images_train'
CAMERA_NAME = 'BlenderNeRF Camera'

# camera on sphere operator class
class CameraOnSphere(blender_nerf_operator.BlenderNeRF_Operator):
    '''Camera on Sphere Operator'''
    bl_idname = 'object.camera_on_sphere'
    bl_label = 'Camera on Sphere COS'

    def execute(self, context):
        scene = context.scene
        camera = scene.camera

        # check if camera is selected : next errors depend on an existing camera
        if camera == None:
            self.report({'ERROR'}, 'Be sure to have a selected camera!')
            return {'FINISHED'}

        # if there is an error, print first error message
        error_messages = self.asserts(scene, method='COS')
        if len(error_messages) > 0:
           self.report({'ERROR'}, error_messages[0])
           return {'FINISHED'}

        output_data = self.get_camera_intrinsics(scene, camera)

        # clean directory name (unsupported characters replaced) and output path
        output_dir = bpy.path.clean_name(scene.cos_dataset_name)
        output_path = os.path.join(scene.save_path, output_dir)

        # initial property might have changed since set_init_props update
        scene.init_output_path = scene.render.filepath

        # other intial properties
        scene.init_sphere_exists = scene.show_sphere
        scene.init_camera_exists = scene.show_camera
        scene.init_frame_start = scene.frame_start
        scene.init_frame_end = scene.frame_end
        scene.init_active_camera = camera

        if scene.test_data:
            output_test_path = os.path.join(output_path, '%s_test' % output_dir)
            os.makedirs(output_test_path, exist_ok=True)

            # testing transforms
            output_data['frames'] = self.get_camera_extrinsics(scene, camera, mode='TEST', method='COS')
            self.save_json(output_test_path, 'transforms_test.json', output_data)

        if scene.train_data:
            if not scene.show_camera: scene.show_camera = True

            # train camera on sphere
            sphere_camera = scene.objects[CAMERA_NAME]
            sphere_output_data = self.get_camera_intrinsics(scene, sphere_camera)
            scene.camera = sphere_camera

            output_train_path = os.path.join(output_path, '%s_train' % output_dir)
            output_train = os.path.join(output_train_path, OUTPUT_TRAIN)
            os.makedirs(output_train, exist_ok=True)

            # training transforms
            sphere_output_data['frames'] = self.get_camera_extrinsics(scene, sphere_camera, mode='TRAIN', method='COS')
            self.save_json(output_train_path, 'transforms_train.json', sphere_output_data)

            # rendering
            if scene.render_frames:
                scene.rendering = (False, False, True)
                scene.frame_start = 1 # update start frame
                scene.frame_end = scene.nb_frames # update end frame
                scene.render.filepath = os.path.join(output_train, '') # training frames path
                bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True) # render scene

        # if frames are rendered, the below code is executed by the handler function
        if not any(scene.rendering):
            # compress dataset and remove folder (only keep zip)
            shutil.make_archive(output_path, 'zip', output_path) # output filename = output_path
            shutil.rmtree(output_path)

        return {'FINISHED'}