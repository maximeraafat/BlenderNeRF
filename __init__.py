import bpy
from bpy.app.handlers import persistent
from . import sof_ui, sof_operator


bl_info = {
    'name': 'Blender x NeRF',
    'description': 'Simple and quick dataset creation tool to use NeRF',
    'author': 'Maxime Raafat',
    'version': (1, 0, 0),
    'blender': (3, 0, 0),
    'location': '3D View > N panel > Blender x NeRF',
    'warning': 'T.B.D.',
    'doc_url': 'upcoming github repository',
    'category': 'Object',
}


# global addon script variable
OUTPUT_DIR = 'nerf_dataset'

# addon blender properties
PROPS = [
    ('train_frame_steps', bpy.props.IntProperty(name='Frame Step', description='Number of frames to skip forward for the NeRF training dataset created while rendering/playing back each frame', default=3, soft_min=1) ),
    ('render_frames', bpy.props.BoolProperty(name='Render Frames', description='Whether the training frames for NeRF should be rendered or not, in which case only the transforms.json files will be generated', default=True) ),
    ('save_path', bpy.props.StringProperty(name='Save Path', description='Output Directory. The training and testing data will be stored under <save path>/%s' % OUTPUT_DIR, subtype='DIR_PATH') ),
    ('aabb', bpy.props.IntProperty(name='AABB', description='AABB scale as defined in Instant NGPs NeRF version', default=4, soft_min=1, soft_max=128) ),
    ('train_data', bpy.props.BoolProperty(name='Train', description='Construct training data', default=True) ),
    ('test_data', bpy.props.BoolProperty(name='Test', description='Construct testing data', default=True) ),

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
def set_to_init(scene):
    scene.frame_step = scene.init_frame_step
    scene.render.filepath = scene.init_output_path

# set initial property values (bpy.data and bpy.context require a loaded scene)
@persistent
def set_init_props(scene):
    filepath = bpy.data.filepath
    filename = bpy.path.basename(filepath)
    default_save_path = filepath[:-len(filename)] # remove file name from blender file path = directoy path

    scene.save_path = default_save_path
    scene.init_frame_step = bpy.context.scene.frame_step
    scene.init_output_path = bpy.context.scene.render.filepath


# load addon
def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for cls in CLASSES:
        bpy.utils.register_class(cls)

    bpy.app.handlers.render_complete.append(set_to_init)
    bpy.app.handlers.render_cancel.append(set_to_init)
    bpy.app.handlers.load_post.append(set_init_props)

# deregister addon
def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.render_complete.remove(set_to_init)
    bpy.app.handlers.render_cancel.remove(set_to_init)
    bpy.app.handlers.load_post.remove(set_init_props)


if __name__ == '__main__':
    register()
