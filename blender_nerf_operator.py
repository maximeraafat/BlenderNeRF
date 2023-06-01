import os
import math
import json
import bpy


# global addon script variables
OUTPUT_TRAIN = 'images_train'
OUTPUT_TEST = 'images_test'


# helper function
def listify_matrix(matrix):
    matrix_list = []
    for row in matrix:
        matrix_list.append(list(row))
    return matrix_list


# blender nerf operator parent class
class BlenderNeRF_Operator(bpy.types.Operator):

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

        K = [[s_u, 0, optical_center_x],
             [0, s_v, optical_center_y],
             [0, 0, 1]]

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
            'K': K,
            'aabb_scale': scene.aabb
        }

        return camera_intr_dict

    # camera extrinsics (transform matrices)
    def get_camera_extrinsics(self, scene, camera, mode='TRAIN', method='SOF'):
        assert mode == 'TRAIN' or mode == 'TEST'
        assert method == 'SOF' or method == 'TTC' or method == 'COS' or method == 'DFC'

        scene.camera = camera
        initFrame = scene.frame_current
        step = scene.train_frame_steps if (mode == 'TRAIN' and method == 'SOF') else scene.frame_step

        camera_extr_dict = []
        if method != "DFC":
            for frame in range(scene.frame_start, scene.frame_end + 1, step):
                scene.frame_set(frame)
                filename = os.path.basename( scene.render.frame_path(frame=frame) )
                filedir = OUTPUT_TRAIN * (mode == 'TRAIN') + OUTPUT_TEST * (mode == 'TEST')
                filepath = os.path.join(filedir, filename)
                frame_data = {
                    'file_path': filepath,
                    'transform_matrix': listify_matrix( camera.matrix_world )
                }

                camera_extr_dict.append(frame_data)

            scene.frame_set(initFrame) # set back to initial frame

            return camera_extr_dict
        else:
            filedir = OUTPUT_TRAIN * (mode == 'TRAIN') + OUTPUT_TEST * (mode == 'TEST')
            filepath = os.path.join(filedir, f"{camera.name}.png")
            frame_data = {
                'file_path': filepath,
                'transform_matrix': listify_matrix( camera.matrix_world )
            }
            camera_extr_dict.append(frame_data)
            return camera_extr_dict

    def save_json(self, directory, filename, data, indent=4):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=indent)

    def is_power_of_two(self, x):
        return math.log2(x).is_integer()

    def asserts(self, scene, method='SOF'):
        assert method == 'SOF' or method == 'TTC' or method == 'COS' or method == 'DFC'

        camera = scene.camera
        train_camera = scene.camera_train_target
        test_camera = scene.camera_test_target

        error_messages = []

        if method == 'SOF':
            if not camera.data.type == 'PERSP':
                error_messages.append('Only perspective cameras are supported!')
            if scene.sof_dataset_name == '':
                error_messages.append('Dataset name cannot be empty!')
        elif method == 'TTC':
            if not (train_camera.data.type == 'PERSP' and test_camera.data.type == 'PERSP'):
                error_messages.append('Only perspective cameras are supported!')
            if scene.ttc_dataset_name == '':
                error_messages.append('Dataset name cannot be empty!')

        if not self.is_power_of_two(scene.aabb):
            error_messages.append('AABB scale needs to be a power of two!')

        if scene.save_path == '':
            error_messages.append('Save path cannot be empty!')

        return error_messages
