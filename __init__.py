import bpy
from . import helper, blender_nerf_ui, sof_ui, ttc_ui, cos_ui, sof_operator, ttc_operator, cos_operator


# blender info
bl_info = {
    'name': 'BlenderNeRF',
    'description': 'Easy NeRF synthetic dataset creation within Blender',
    'author': 'Maxime Raafat',
    'version': (6, 0, 0),
    'blender': (4, 0, 0),
    'location': '3D View > N panel > BlenderNeRF',
    'doc_url': 'https://github.com/maximeraafat/BlenderNeRF',
    'category': 'Object',
}

# global addon script variables
TRAIN_CAM = 'Train Cam'
TEST_CAM = 'Test Cam'
VERSION = '.'.join(str(x) for x in bl_info['version'])

# addon blender properties
PROPS = [
    # global controllable properties
    ('train_data', bpy.props.BoolProperty(name='Train', description='Construct the training data', default=True) ),
    ('test_data', bpy.props.BoolProperty(name='Test', description='Construct the testing data', default=True) ),
    ('aabb', bpy.props.IntProperty(name='AABB', description='AABB scale as defined in Instant NGP', default=4, soft_min=1, soft_max=128) ),
    ('render_frames', bpy.props.BoolProperty(name='Render Frames', description='Whether training frames should be rendered. If not selected, only the transforms.json files will be generated', default=True) ),
    ('logs', bpy.props.BoolProperty(name='Save Log File', description='Whether to create a log file containing information on the BlenderNeRF run', default=False) ),
    ('splats', bpy.props.BoolProperty(name='Gaussian Points', description='Whether to export a points3d.ply file for Gaussian Splatting', default=False) ),
    ('splats_test_dummy', bpy.props.BoolProperty(name='Dummy Test Camera', description='Whether to export a dummy test transforms.json file or the full set of test camera poses', default=True) ),
    ('nerf', bpy.props.BoolProperty(name='NeRF', description='Whether to export the camera transforms.json files in the defaut NeRF file format convention', default=False) ),
    ('save_path', bpy.props.StringProperty(name='Save Path', description='Path to the output directory in which the synthetic dataset will be stored', subtype='DIR_PATH') ),

    # global automatic properties
    ('init_frame_step', bpy.props.IntProperty(name='Initial Frame Step') ),
    ('init_output_path', bpy.props.StringProperty(name='Initial Output Path', subtype='DIR_PATH') ),
    ('rendering', bpy.props.BoolVectorProperty(name='Rendering', description='Whether one of the SOF, TTC or COS methods is rendering', default=(False, False, False), size=3) ),
    ('blendernerf_version', bpy.props.StringProperty(name='BlenderNeRF Version', default=VERSION) ),

    # sof properties
    ('sof_dataset_name', bpy.props.StringProperty(name='Name', description='Name of the SOF dataset : the data will be stored under <save path>/<name>', default='dataset') ),
    ('train_frame_steps', bpy.props.IntProperty(name='Frame Step', description='Frame step N for the captured training frames. Every N-th frame will be used for training NeRF', default=3, soft_min=1) ),

    # ttc properties
    ('ttc_dataset_name', bpy.props.StringProperty(name='Name', description='Name of the TTC dataset : the data will be stored under <save path>/<name>', default='dataset') ),
    ('ttc_nb_frames', bpy.props.IntProperty(name='Frames', description='Number of training frames from the training camera', default=100, soft_min=1) ),
    ('camera_train_target', bpy.props.PointerProperty(type=bpy.types.Object, name=TRAIN_CAM, description='Pointer to the training camera', poll=helper.poll_is_camera) ),
    ('camera_test_target', bpy.props.PointerProperty(type=bpy.types.Object, name=TEST_CAM, description='Pointer to the testing camera', poll=helper.poll_is_camera) ),

    # cos controllable properties
    ('cos_dataset_name', bpy.props.StringProperty(name='Name', description='Name of the COS dataset : the data will be stored under <save path>/<name>', default='dataset') ),
    ('sphere_location', bpy.props.FloatVectorProperty(name='Location', description='Center position of the training sphere', unit='LENGTH', update=helper.properties_ui_upd) ),
    ('sphere_rotation', bpy.props.FloatVectorProperty(name='Rotation', description='Rotation of the training sphere', unit='ROTATION', update=helper.properties_ui_upd) ),
    ('sphere_scale', bpy.props.FloatVectorProperty(name='Scale', description='Scale of the training sphere in xyz axes', default=(1.0, 1.0, 1.0), update=helper.properties_ui_upd) ),
    ('sphere_radius', bpy.props.FloatProperty(name='Radius', description='Radius scale of the training sphere', default=4.0, soft_min=0.01, unit='LENGTH', update=helper.properties_ui_upd) ),
    ('focal', bpy.props.FloatProperty(name='Lens', description='Focal length of the training camera', default=50, soft_min=1, soft_max=5000, unit='CAMERA', update=helper.properties_ui_upd) ),
    ('seed', bpy.props.IntProperty(name='Seed', description='Random seed for sampling views on the training sphere', default=0) ),
    ('cos_nb_frames', bpy.props.IntProperty(name='Frames', description='Number of training frames randomly sampled from the training sphere', default=100, soft_min=1) ),
    ('show_sphere', bpy.props.BoolProperty(name='Sphere', description='Whether to show the training sphere from which random views will be sampled', default=False, update=helper.visualize_sphere) ),
    ('show_camera', bpy.props.BoolProperty(name='Camera', description='Whether to show the training camera', default=False, update=helper.visualize_camera) ),
    ('upper_views', bpy.props.BoolProperty(name='Upper Views', description='Whether to sample views from the upper hemisphere of the training sphere only', default=False) ),
    ('outwards', bpy.props.BoolProperty(name='Outwards', description='Whether to point the camera outwards of the training sphere', default=False, update=helper.properties_ui_upd) ),

    # cos automatic properties
    ('sphere_exists', bpy.props.BoolProperty(name='Sphere Exists', description='Whether the sphere exists', default=False) ),
    ('init_sphere_exists', bpy.props.BoolProperty(name='Init sphere exists', description='Whether the sphere initially exists', default=False) ),
    ('camera_exists', bpy.props.BoolProperty(name='Camera Exists', description='Whether the camera exists', default=False) ),
    ('init_camera_exists', bpy.props.BoolProperty(name='Init camera exists', description='Whether the camera initially exists', default=False) ),
    ('init_active_camera', bpy.props.PointerProperty(type=bpy.types.Object, name='Init active camera', description='Pointer to initial active camera', poll=helper.poll_is_camera) ),
    ('init_frame_end', bpy.props.IntProperty(name='Initial Frame End') ),
]

# classes to register / unregister
CLASSES = [
    blender_nerf_ui.BlenderNeRF_UI,
    sof_ui.SOF_UI,
    ttc_ui.TTC_UI,
    cos_ui.COS_UI,
    sof_operator.SubsetOfFrames,
    ttc_operator.TrainTestCameras,
    cos_operator.CameraOnSphere
]

# load addon
def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.app.handlers.render_complete.append(helper.post_render)
    bpy.app.handlers.render_cancel.append(helper.post_render)
    bpy.app.handlers.frame_change_post.append(helper.cos_camera_update)
    bpy.app.handlers.depsgraph_update_post.append(helper.properties_desgraph_upd)
    bpy.app.handlers.depsgraph_update_post.append(helper.set_init_props)

# deregister addon
def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    bpy.app.handlers.render_complete.remove(helper.post_render)
    bpy.app.handlers.render_cancel.remove(helper.post_render)
    bpy.app.handlers.frame_change_post.remove(helper.cos_camera_update)
    bpy.app.handlers.depsgraph_update_post.remove(helper.properties_desgraph_upd)
    # bpy.app.handlers.depsgraph_update_post.remove(helper.set_init_props)

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()