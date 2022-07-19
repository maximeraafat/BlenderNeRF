import os
import shutil
import bpy
from bpy.app.handlers import persistent
from . import blender_nerf_ui, sof_ui, ttc_ui, sof_operator, ttc_operator


bl_info = {
    'name': 'Blender x NeRF',
    'description': 'Simple and quick NeRF dataset creation tool',
    'author': 'Maxime Raafat',
    'version': (2, 0, 0),
    'blender': (3, 0, 0),
    'location': '3D View > N panel > BlenderNeRF',
    'doc_url': 'https://github.com/maximeraafat/BlenderNeRF',
    'category': 'Object',
}


# camera pointer property poll function
def poll_is_camera(self, obj):
    return obj.type == 'CAMERA'

# global addon script variables
TRAIN_CAM = 'Train Cam'
TEST_CAM = 'Test Cam'

# addon blender properties
PROPS = [
    # global manually defined properties
    ('train_data', bpy.props.BoolProperty(name='Train', description='Construct training data', default=True) ),
    ('test_data', bpy.props.BoolProperty(name='Test', description='Construct testing data', default=True) ),
    ('aabb', bpy.props.IntProperty(name='AABB', description='AABB scale as defined in Instant NGPs NeRF version', default=4, soft_min=1, soft_max=128) ),
    ('render_frames', bpy.props.BoolProperty(name='Render Frames', description='Whether the training frames for NeRF should be rendered or not, in which case only the transforms.json files will be generated', default=True) ),
    ('save_path', bpy.props.StringProperty(name='Save Path', description='Path to the output directory in which the dataset will be stored', subtype='DIR_PATH') ),

    # global automatically defined properties
    ('init_frame_step', bpy.props.IntProperty(name='Initial Frame Step') ),
    ('init_output_path', bpy.props.StringProperty(name='Initial Output Path', subtype='DIR_PATH') ),
    ('is_rendering', bpy.props.BoolVectorProperty(name='Method Rendering?', description='Whether SOF, TTC or COS is rendering', default=(False, False, False), size=3) ),

    # sof properties
    ('sof_dataset_name', bpy.props.StringProperty(name='Name', description='Name of the SOF dataset : the data will be stored under <save path>/<name>', default='dataset') ),
    ('train_frame_steps', bpy.props.IntProperty(name='Frame Step', description='Number of frames to skip forward for the NeRF training dataset created while rendering/playing back each frame', default=3, soft_min=1) ),

    # ttc properties
    ('ttc_dataset_name', bpy.props.StringProperty(name='Name', description='Name of the TTC dataset : the data will be stored under <save path>/<name>', default='dataset') ),
    ('camera_train_target', bpy.props.PointerProperty(type=bpy.types.Object, name=TRAIN_CAM, description='Pointer to training camera', poll=poll_is_camera) ),
    ('camera_test_target', bpy.props.PointerProperty(type=bpy.types.Object, name=TEST_CAM, description='Pointer to testing camera', poll=poll_is_camera) ),
]

# classes to register / unregister
CLASSES = [
    blender_nerf_ui.BlenderNeRF_UI,
    sof_ui.SOF_UI,
    ttc_ui.TTC_UI,
    sof_operator.SubsetOfFrames,
    ttc_operator.TrainTestCameras
]


## blender handler functions

# set frame step and filepath back to initial
@persistent
def post_render(scene):
    if any(scene.is_rendering): # execute this function only when rendering with addon
        scene.is_rendering = (False, False, False)
        scene.frame_step = scene.init_frame_step
        scene.render.filepath = scene.init_output_path

        method_dataset_name = scene.sof_dataset_name if scene.is_rendering[0] else scene.ttc_dataset_name

        # clean directory name (unsupported characters replaced) and output path
        output_dir = bpy.path.clean_name(method_dataset_name)
        output_path = os.path.join(scene.save_path, output_dir)

        # compress dataset and remove folder (only keep zip)
        shutil.make_archive(output_path, 'zip', output_path) # output filename = output_path
        shutil.rmtree(output_path)

# set initial property values (bpy.data and bpy.context require a loaded scene)
@persistent
def set_init_props(scene):
    scene.init_frame_step = scene.frame_step
    scene.init_output_path = scene.render.filepath

    # set save_path to path in which blender file is stored
    # filepath = bpy.data.filepath
    # filename = bpy.path.basename(filepath)
    # default_save_path = filepath[:-len(filename)] # remove file name from blender file path = directoy path
    # scene.save_path = default_save_path

    bpy.app.handlers.depsgraph_update_post.remove(set_init_props)


# load addon
def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.app.handlers.render_complete.append(post_render)
    bpy.app.handlers.render_cancel.append(post_render)
    bpy.app.handlers.depsgraph_update_post.append(set_init_props)

# deregister addon
def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    bpy.app.handlers.render_complete.remove(post_render)
    bpy.app.handlers.render_cancel.remove(post_render)
    # bpy.app.handlers.depsgraph_update_post.remove(set_init_props)

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
