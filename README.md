# BlenderNeRF

[**BlenderNeRF**](https://github.com/maximeraafat/BlenderNeRF) allows you to easily create custom datasets in Blender. This plugin enables easy camera path selection, rendering and dataset formatting in Blender. The original [repo](https://github.com/maximeraafat/BlenderNeRF) by maximeraafat included two file formats: InstantNGP and NeRF. This one has been modified to replace NeRF with [nerfstudio](https://docs.nerf.studio/en/latest/), a simple API allowing for simplified creating, training and visualizing NeRFs. Most of the functionality remains the same from the original [repo](https://github.com/maximeraafat/BlenderNeRF), but the second option now allows for seamless usage of the dataset to nerfstudio.


## Installation

1. Download this repository as a ZIP file
2. Open Blender (3.0.0 or above)
3. In Blender, head to **Edit > Preferences > Add-ons**, and click **Install...**
4. Select the downloaded **ZIP** file, and activate the add-on (**Object: BlenderNeRF**)

Although release versions of **BlenderNeRF** are available for download, they are primarily intended for tracking major code changes and for citation purposes. I recommend dowloading the current repository directly, since minor changes or bug fixes might not be included in a release right away.


## Setting

**BlenderNeRF** consists of 3 methods discussed in the sub-sections below. Each method is capable of creating **training** data and **testing** data for NeRF in the form of images and a `transforms.json` file. For training, images are stored in an `images` directory whereas test images are stored in `test_images` directory. Similarly, for training, we have a `transforms.json` file whereas for testing we have a `transforms_test.json` file with the corresponding camera information. The data is archived into a single **ZIP** file containing training and testing folders. Training data can then be used by a NeRF model to learn the 3D scene representation. Once trained, the model may be evaluated (or tested) on the testing data (camera information only) to obtain novel renders.

### Subset of Frames

**Subset of Frames (SOF)** renders every **N** frames from a camera animation, and utilises the rendered subset of frames as NeRF training data. The registered testing data spans over all frames of the same camera amimation, including training frames. When trained, the NeRF model can render the full camera animation and is consequently well suited for rendering large animation of static scenes.

### Train and Test Cameras

**Train and Test Cameras (TTC)** registers training and testing data from two separate user defined cameras. A NeRF model can then be fitted with the data extracted from the training camera, and be evaluated on the testing data.

### Camera on Sphere

**Camera on Sphere (COS)** renders training frames by uniformly sampling random camera views directed at the center from a user controlled sphere. Testing data is extracted from a selected camera.


## How to use the Methods

The add-on properties panel is available under `3D View > N panel > BlenderNeRF` (the **N panel** is accessible under the 3D viewport when pressing `N`). All 3 methods (**SOF**, **TTC** and **COS**) share a common tab called `BlenderNeRF shared UI` with the below listed controllable properties.

* `Train` (activated by default) : whether to register training data (renderings + camera information)
* `Test` (activated by default) : whether to register testing data (camera information only)
* `AABB` (by default set to **4**) : aabb scale parameter as described in Instant NGP (more details below)
* `Render Frames` (activated by default) : whether to render the frames
* `Save Log File` (deactivated by default) : whether to save a log file containing reproducibility information on the **BlenderNeRF** run
* `File Format` (**NGP** by default) : whether to export the camera files in the Instant NGP or nerfstudio file format convention
* `Save Path` (empty by default) : path to the output directory in which the dataset will be created

`AABB` is restricted to be an integer power of 2, it defines the side length of the bounding box volume in which NeRF will trace rays. The property was introduced with **NVIDIA's [Instant NGP](https://github.com/NVlabs/instant-ngp)** version of NeRF.

The `File Format` property can either be **NGP** or **nerfstudio**. Both the **NGP** and the **nerfstudio** file format convention are similar, with a few additional parameters which can be accessed by Instant NGP.

Notice that each method has its distinctive `Name` property (by default set to `dataset`) corresponding to the dataset name and created **ZIP** filename for the respective method. Please note that unsupported characters, such as spaces, `#` or `/`, will automatically be replaced by an underscore.

Below are described the properties specific to each method (the `Name` property is left out, since already discussed above).

### How to use Subset of Frames (SOF) Method

* `Frame Step` (by default set to **3**) : **N** (as defined in the [Setting](#setting) section) = frequency at which the training frames are registered
* `Camera` (always set to the active camera) : camera used for registering training and testing data
* `PLAY SOF` : play the **Subset of Frames** method

### How to use Train and Test Cameras (TTC) Method

* `Train Cam` (empty by default) : camera used for registering the training data
* `Test Cam` (empty by default) : camera used for registering the testing data
* `PLAY TTC` : play the **Train and Test Cameras** method

### How to Camera on Sphere (COS) Method

* `Camera` (always set to the active camera) : camera used for registering the testing data
* `Location` (by default set to **0m** vector) : center position of the training sphere from which camera views are sampled
* `Rotation` (by default set to **0°** vector) : rotation of the training sphere from which camera views are sampled
* `Scale` (by default set to **1** vector) : scale vector of the training sphere in xyz axes
* `Radius` (by default set to **4m**) : radius scalar of the training sphere
* `Lens` (by default set to **50mm**) : focal length of the training camera
* `Seed` (by default set to **0**) : seed to initialize the random camera view sampling procedure
* `Frames` (by default set to **100**) : number of training frames sampled and rendered from the training sphere
* `Sphere` (deactivated by default) : whether to show the training sphere from which random views will be sampled
* `Camera` (deactivated by default) : whether to show the camera used for registering the training data
* `Upper Views` (deactivated by default) : whether to sample views from the upper training hemisphere only (rotation variant)
* `Outwards` (deactivated by default) : whether to point the camera outwards of the training sphere
* `PLAY COS` : play the **Camera on Sphere** method

Note that activating the `Sphere` and `Camera` properties creates a `BlenderNeRF Sphere` empty object and a `BlenderNeRF Camera` camera object respectively. Please do not create any objects with these names manually, since this might break the add-on functionalities.

`Frames` amount of training frames will be captured using the `BlenderNeRF Camera` object, starting from the scene start frame. Finally, keep in mind that the training camera is locked in place and cannot manually be moved.


## Tips for optimal results

NVIDIA provides a few helpful tips on how to train a NeRF model using [Instant NGP](https://github.com/NVlabs/instant-ngp/blob/master/docs/nerf_dataset_tips.md). Feel free to visit their repository for further help. Below are some quick tips for optimal **nerfing**.

* NeRF trains best with 50 to 150 images
* Testing views should not deviate too much from training views
* Scene movement, motion blur or blurring artefacts can degrade the reconstruction quality
* The captured scene should be at least one Blender unit away from the camera
* Keep `AABB` as tight as possible to the scene scale, higher values will slow down training
* If the reconstruction quality appears blurry, start by adjusting `AABB` while keeping it a power of 2
* Avoid adjusting the camera focal lengths during the animation, the vanilla NeRF methods do not support multiple focal lengths


## Citation

Please consider citing the original **BlenderNeRF** repo and share some of your work using the `#blendernerf` hashtag on social media!
