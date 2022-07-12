import os
import math
import json
import shutil
import bpy


# global addon script variables
OUTPUT_TRAIN = 'images_train'
OUTPUT_TEST = 'images_test'


## helper functions

def is_power_of_two(x):
    return math.log2(x).is_integer()

def listify_matrix(matrix):
    matrix_list = []
    for row in matrix:
        matrix_list.append(list(row))
    return matrix_list


# subset of frames operator class
class SubsetOfFrames(bpy.types.Operator):
    '''Subset of Frames Operator'''
    bl_idname = 'object.subset_of_frames'
    bl_label = 'Subset of Frames SOF'

    # camera intrinsics and other relevant camera data
    # https://blender.stackexchange.com/questions/38009/3x4-camera-matrix-from-blender-camera
    def get_camera_intrinsics(self, scene, camera):
        camera_angle_x = camera.data.angle_x
        camera_angle_y = camera.data.angle_y

        f_in_mm = camera.data.lens
        scale = scene.render.resolution_percentage / 100
        pixel_aspect_ratio = scene.render.pixel_aspect_y / scene.render.pixel_aspect_x
        width_res_in_px = scene.render.resolution_x * scale
        height_res_in_px = scene.render.resolution_y * scale

        optical_center_x = width_res_in_px / 2
        optical_center_y = height_res_in_px / 2

        sensor_size_in_mm = camera.data.sensor_height if camera.data.sensor_fit == 'VERTICAL' else camera.data.sensor_width

        size_x = scene.render.pixel_aspect_x * width_res_in_px
        size_y = scene.render.pixel_aspect_y * height_res_in_px

        if camera.data.sensor_fit == 'AUTO':
            sensor_fit = 'HORIZONTAL' if size_x >= size_y else 'VERTICAL'
        else :
            sensor_fit = camera.data.sensor_fit

        view_fac_in_px = width_res_in_px if sensor_fit == 'HORIZONTAL' else pixel_aspect_ratio * height_res_in_px
        pixel_size_mm_per_px = sensor_size_in_mm / f_in_mm / view_fac_in_px

        s_u = 1 / pixel_size_mm_per_px
        s_v = 1 / pixel_size_mm_per_px / pixel_aspect_ratio

        camera_intr_dict = {
            'camera_angle_x': camera_angle_x,
            'camera_angle_y': camera_angle_y,
            'fl_x': s_u,
            'fl_y': s_v,
            'k1': 0.0,
            'k2': 0.0,
            'p1': 0.0,
            'p2': 0.0,
            'cx': optical_center_x,
            'cy': optical_center_y,
            'w': width_res_in_px,
            'h': height_res_in_px,
            'aabb_scale': scene.aabb
        }

        return camera_intr_dict

    # camera extrinsics (transform matrices)
    def get_camera_extrinsics(self, scene, camera, mode='TRAIN'):
        assert mode == 'TRAIN' or mode == 'TEST'

        initFrame = scene.frame_current
        step = scene.train_frame_steps if mode == 'TRAIN' else scene.frame_step

        camera_extr_dict = []
        for frame in range(scene.frame_start, scene.frame_end + 1, step):
            scene.frame_set(frame)
            filename = os.path.basename( scene.render.frame_path(frame=frame) )
            filedir = OUTPUT_TRAIN * (mode == 'TRAIN') + OUTPUT_TEST * (mode == 'TEST')

            frame_data = {
                'file_path': os.path.join(filedir, filename),
                'transform_matrix': listify_matrix( camera.matrix_world )
            }

            camera_extr_dict.append(frame_data)

        scene.frame_set(initFrame) # set back to initial frame

        return camera_extr_dict

    def save_json(self, directory, filename, data, indent=4):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=indent)

    def execute(self, context):
        scene = context.scene
        camera = scene.camera

        if not camera.data.type == 'PERSP':
            self.report({'ERROR'}, 'Only perspective cameras are supported!')
            return {'FINISHED'}

        if scene.save_path == '':
            self.report({'ERROR'}, 'Save path cannot be empty!')
            return {'FINISHED'}

        if not is_power_of_two(scene.aabb):
            self.report({'ERROR'}, 'AABB scale needs to be a power of two!')
            return {'FINISHED'}

        output_data = self.get_camera_intrinsics(scene, camera)

        # clean directory name (unsupported characters replaced) and output path
        output_dir = bpy.path.clean_name(scene.dataset_name)
        output_path = os.path.join(scene.save_path, output_dir)

        # initial property values might have changed since depsgraph_update_post handler
        scene.init_frame_step = scene.frame_step
        scene.init_output_path = scene.render.filepath

        if scene.test_data:
            output_test_path = os.path.join(output_path, '%s_test' % output_dir)
            os.makedirs(output_test_path, exist_ok=True)

            # testing transforms
            output_data['frames'] = self.get_camera_extrinsics(scene, camera, mode='TEST')
            self.save_json(output_test_path, 'transforms_test.json', output_data)

        if scene.train_data:
            output_train_path = os.path.join(output_path, '%s_train' % output_dir)
            output_train = os.path.join(output_train_path, OUTPUT_TRAIN)
            os.makedirs(output_train, exist_ok=True)

            # training transforms
            output_data['frames'] = self.get_camera_extrinsics(scene, camera, mode='TRAIN')
            self.save_json(output_train_path, 'transforms_train.json', output_data)

            if scene.render_frames:
                scene.frame_step = scene.train_frame_steps # update frame step
                scene.render.filepath = os.path.join(output_train, '') # training frames path
                bpy.ops.render.render('INVOKE_DEFAULT', animation=True, write_still=True) # render scene

        # if frames are rendered, the below code is executed by the handler function
        if not scene.render_frames:
            # compress dataset and remove folder (only keep zip)
            shutil.make_archive(output_path, 'zip', output_path) # output filename = output_path
            shutil.rmtree(output_path)

        return {'FINISHED'}
