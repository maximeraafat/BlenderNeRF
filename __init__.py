import os
import shutil
import bpy
from bpy.app.handlers import persistent
from . import sof_ui, sof_operator


bl_info = {
    'name': 'Blender x NeRF',
    'description': 'Simple and quick NeRF dataset creation tool',
    'author': 'Maxime Raafat',
    'version': (1, 0, 0),
    'blender': (3, 0, 0),
    'location': '3D View > N panel > Blender x NeRF',
    'doc_url': 'https://github.com/maximeraafat/BlenderNeRF',
    'category': 'Object',
}


# addon blender properties
PROPS = [
    ('train_frame_steps', bpy.props.IntProperty(name='Frame Step', description='Number of frames to skip forward for the NeRF training dataset created while rendering/playing back each frame', default=3, soft_min=1) ),
    ('render_frames', bpy.props.BoolProperty(name='Render Frames', description='Whether the training frames for NeRF should be rendered or not, in which case only the transforms.json files will be generated', default=True) ),
    ('save_path', bpy.props.StringProperty(name='Save Path', description='Path to the output directory in which the dataset will be stored', subtype='DIR_PATH') ),
    ('dataset_name', bpy.props.StringProperty(name='Name', description='Name of the dataset : the data will be stored under <save path>/<name>', default='dataset') ),
    ('aabb', bpy.props.IntProperty(name='AABB', description='AABB scale as defined in Instant NGPs NeRF version', default=4, soft_min=1, soft_max=128) ),
    ('train_data', bpy.props.BoolProperty(name='Train', description='Construct training data', default=True) ),
    ('test_data', bpy.props.BoolProperty(name='Test', description='Construct testing data', default=True) ),

    ('is_rendering', bpy.props.BoolProperty(name='Is Rendering?', default=False) ),
    ('init_frame_step', bpy.props.IntProperty(name='Init Frame Step') ),
    ('init_output_path', bpy.props.StringProperty(name='Init Output Path', subtype='DIR_PATH') ),
]

# classes to register / unregister
CLASSES = [
    sof_ui.SOF_UI,
    sof_operator.SubsetOfFrames
]


## blender handler functions

# set frame step and filepath back to initial
@persistent
def post_render(scene):
    if scene.is_rendering: # execute this function only when rendering with addon
        scene.frame_step = scene.init_frame_step
        scene.render.filepath = scene.init_output_path

        # clean directory name (unsupported characters replaced) and output path
        output_dir = bpy.path.clean_name(scene.dataset_name)
        output_path = os.path.join(scene.save_path, output_dir)

        # compress dataset and remove folder (only keep zip)
        shutil.make_archive(output_path, 'zip', output_path) # output filename = output_path
        shutil.rmtree(output_path)

# set initial property values (bpy.data and bpy.context require a loaded scene)
@persistent
def set_init_props(scene):
    filepath = bpy.data.filepath
    filename = bpy.path.basename(filepath)
    default_save_path = filepath[:-len(filename)] # remove file name from blender file path = directoy path

    scene.save_path = default_save_path
    scene.init_frame_step = scene.frame_step
    scene.init_output_path = scene.render.filepath

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
