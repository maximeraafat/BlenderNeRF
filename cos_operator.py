import os
import shutil
import bpy
import math
import mathutils
import random
import numpy as np


def create_collection(collection_name, num_cameras, radius, above_horizon_only):
    collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(collection)
    for i in range(num_cameras):
        theta = random.uniform(0, 2 * math.pi)
        phi = math.acos(random.uniform(-1, 1))
        x = radius * math.sin(phi) * math.cos(theta)
        y = radius * math.sin(phi) * math.sin(theta)
        z = radius * math.cos(phi)

        if above_horizon_only:
            z = abs(z)

        direction = mathutils.Vector((-x, -y, -z))
        direction.normalize()
        rot_quat = direction.to_track_quat('-Z', 'Y')
        # (0, 0, 0) is facing top-down
        # we want to face the origin
        camera = bpy.data.cameras.new('COS_Camera')
        camera_ob = bpy.data.objects.new('COS_Camera', camera)
        camera_ob.location = (x, y, z)
        camera_ob.rotation_euler = rot_quat.to_euler()
        collection.objects.link(camera_ob)
    return collection


class RandomCamerasAroundOrigin(bpy.types.Operator):
    """Random Cameras Around Origin Operator
    Given a radius and a number n, this operator will randomly create
    n cameras that faces the origin on the sphere of radius r around the origin, and leave them selected.
    """
    bl_idname = 'object.random_cameras_around_origin'
    bl_label = 'Random Cameras Around Origin'

    def execute(self, context):
        scene = context.scene
        radius = scene.cos_radius
        # create new collection for cameras
        create_collection('Train_Cameras', scene.cos_train_num_samples, radius, scene.cos_above_horizon_only)
        create_collection('Test_Cameras', scene.cos_test_num_samples, radius, scene.cos_above_horizon_only)

        return {'FINISHED'}

