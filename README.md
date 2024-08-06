# BlenderNeRF

Whether a VFX artist, a research fellow or a graphics amateur, **BlenderNeRF** is the easiest and fastest way to create synthetic NeRF and Gaussian Splatting datasets within Blender. Obtain renders and camera parameters with a single click, while having full user control over the 3D scene and camera!

<p align='center'>
  <a href="https://youtu.be/C8YuDoU11cg"><img src="https://img.youtube.com/vi/C8YuDoU11cg/maxresdefault.jpg" width='90%'></a>
  <br>
  Are you ready to NeRF? Start with a single click in Blender by checking out <a href="https://youtu.be/C8YuDoU11cg">this tutorial</a>!
</p>


## Neural Radiance Fields

**Neural Radiance Fields ([NeRF](https://www.matthewtancik.com/nerf))** aim at representing a 3D scene as a view dependent volumetric object from 2D images only, alongside their respective camera information. The 3D scene is reverse engineered from the training images with help of a simple neural network.

[**Gaussian Splatting**](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) is a follow-up method for rendering radiance fields in a point-based manner. This representation is highly optimised for GPU rendering and leverages more traditional graphics techniques to achieve high frame rates.

I recommend watching [this YouTube video](https://www.youtube.com/watch?v=YX5AoaWrowY) by **Corridor Crew** for a thrilling investigation on a few use cases and future potential applications of NeRFs.


## Motivation

Rendering is an expensive computation. Photorealistic scenes can take seconds to hours to render depending on the scene complexity, hardware and available software resources.

NeRFs and Gaussian splats can speed up this process, but require camera information typically extracted via cumbersome code. This plugin enables anyone to get renders and cameras with a single click in Blender.

<p align='center'>
  <img src='https://maximeraafat.github.io/assets/posts/blendernerf/BlenderNeRF_compressed.gif' width='90%'/>
</p>


## Installation

1. Download this repository as a **ZIP** file
2. Open Blender (4.0.0 or above)
3. In Blender, head to **Edit > Preferences > Add-ons**, and select **Install From Disk** under the drop icon
4. Select the downloaded **ZIP** file

Although release versions of **BlenderNeRF** are available for download, they are primarily intended for tracking major code changes and for citation purposes. I recommend downloading the current repository directly, since minor changes or bug fixes might not be included in a release right away.


## Setting

**BlenderNeRF** consists of 3 methods discussed in the sub-sections below. Each method is capable of creating **training** data and **testing** data for NeRF in the form of training images and a `transforms_train.json` respectively `transforms_test.json` file with the corresponding camera information. The data is archived into a single **ZIP** file containing training and testing folders. Training data can then be used by a NeRF model to learn the 3D scene representation. Once trained, the model may be evaluated (or tested) on the testing data (camera information only) to obtain novel renders.

### Subset of Frames

**Subset of Frames (SOF)** renders every **N** frames from a camera animation, and utilises the rendered subset of frames as NeRF training data. The registered testing data spans over all frames of the same camera animation, including training frames. When trained, the NeRF model can render the full camera animation and is consequently well suited for interpolating or rendering large animations of static scenes.

<p align='center'>
  <img src='https://maximeraafat.github.io/assets/posts/blendernerf/SOF.gif' width='90%'/>
</p>

### Train and Test Cameras

**Train and Test Cameras (TTC)** registers training and testing data from two separate user defined cameras. A NeRF model can then be fitted with the data extracted from the training camera, and be evaluated on the testing data.

<p align='center'>
  <img src='https://maximeraafat.github.io/assets/posts/blendernerf/TTC.gif' width='90%'/>
</p>

### Camera on Sphere

**Camera on Sphere (COS)** renders training frames by uniformly sampling random camera views directed at the center from a user controlled sphere. Testing data is extracted from a selected camera.

<p align='center'>
  <img src='https://maximeraafat.github.io/assets/posts/blendernerf/COS.gif' width='90%'/>
</p>


## How to use the Methods

The add-on properties panel is available under `3D View > N panel > BlenderNeRF` (the **N panel** is accessible under the 3D viewport when pressing `N`). All 3 methods (**SOF**, **TTC** and **COS**) share a common tab called `BlenderNeRF shared UI` with the below listed controllable properties.

* `Train` (activated by default) : whether to register training data (renderings + camera information)
* `Test` (activated by default) : whether to register testing data (camera information only)
* `AABB` (by default set to **4**) : aabb scale parameter as described in Instant NGP (more details below)
* `Render Frames` (activated by default) : whether to render the frames
* `Save Log File` (deactivated by default) : whether to save a log file containing reproducibility information on the **BlenderNeRF** run
* `File Format` (**NGP** by default) : whether to export the camera files in the Instant NGP or defaut NeRF file format convention
* `Gaussian Points` (deactivated by default) : whether to export a `points3d.ply` file for Gaussian Splatting
* `Gaussian Test Camera Poses` (**Dummy** by default): whether to export a dummy test camera file or the full set of test camera poses (only with `Gaussian Points`)
* `Save Path` (empty by default) : path to the output directory in which the dataset will be created

If the `Gaussian Points` property is active, **BlenderNeRF** will create an additional `points3d.ply` file from all visible meshes (at render time) where each vertex will be used as initialization point. Vertex colors will be stored if available, and set to black otherwise.

The [**Gaussian Splatting**](https://github.com/graphdeco-inria/gaussian-splatting) repository natively supports **NeRF** datasets, but requires both train and test data. The `Dummy` option for the `Gaussian Test Camera Poses` property creates an empty test camera pose file, in the case no test images are needed. The `Full` option exports the default test camera poses, but will require separately rendering a `test` folder containing all the test renders.

`AABB` is restricted to be an integer power of 2, it defines the side length of the bounding box volume in which NeRF will trace rays. The property was introduced with **NVIDIA's [Instant NGP](https://github.com/NVlabs/instant-ngp)** version of NeRF.

The `File Format` property can either be **NGP** or **NeRF**. The **NGP** file format convention is the same as the **NeRF** one, with a few additional parameters which can be accessed by Instant NGP.

Notice that each method has its distinctive `Name` property (by default set to `dataset`) corresponding to the dataset name and created **ZIP** filename for the respective method. Please note that unsupported characters, such as spaces, `#` or `/`, will automatically be replaced by an underscore.

Below are described the properties specific to each method (the `Name` property is left out, since already discussed above).

### How to SOF

* `Frame Step` (by default set to **3**) : **N** (as defined in the [Setting](#setting) section) = frequency at which the training frames are registered
* `Camera` (always set to the active camera) : camera used for registering training and testing data
* `PLAY SOF` : play the **Subset of Frames** method operator to export NeRF data

### How to TTC

* `Frames` (by default set to **100**) : number of training frames used from the training camera
* `Train Cam` (empty by default) : camera used for registering the training data
* `Test Cam` (empty by default) : camera used for registering the testing data
* `PLAY TTC` : play the **Train and Test Cameras** method operator to export NeRF data

`Frames` amount of training frames will be captured using the `Train Cam` object, starting from the scene start frame.

### How to COS

* `Camera` (always set to the active camera) : camera used for registering the testing data
* `Location` (by default set to **0 m** vector) : center position of the training sphere from which camera views are sampled
* `Rotation` (by default set to **0°** vector) : rotation of the training sphere from which camera views are sampled
* `Scale` (by default set to **1** vector) : scale vector of the training sphere in xyz axes
* `Radius` (by default set to **4 m**) : radius scalar of the training sphere
* `Lens` (by default set to **50 mm**) : focal length of the training camera
* `Seed` (by default set to **0**) : seed to initialize the random camera view sampling procedure
* `Frames` (by default set to **100**) : number of training frames sampled and rendered from the training sphere
* `Sphere` (deactivated by default) : whether to show the training sphere from which random views will be sampled
* `Camera` (deactivated by default) : whether to show the camera used for registering the training data
* `Upper Views` (deactivated by default) : whether to sample views from the upper training hemisphere only (rotation variant)
* `Outwards` (deactivated by default) : whether to point the camera outwards of the training sphere
* `PLAY COS` : play the **Camera on Sphere** method operator to export NeRF data

Note that activating the `Sphere` and `Camera` properties creates a `BlenderNeRF Sphere` empty object and a `BlenderNeRF Camera` camera object respectively. Please do not create any objects with these names manually, since this might break the add-on functionalities.

`Frames` amount of training frames will be captured using the `BlenderNeRF Camera` object, starting from the scene start frame. Finally, keep in mind that the training camera is locked in place and cannot manually be moved.


## Tips for Optimal Results

NVIDIA provides a few helpful tips on how to train a NeRF model using [Instant NGP](https://github.com/NVlabs/instant-ngp/blob/master/docs/nerf_dataset_tips.md). Feel free to visit their repository for further help. Below are some quick tips for optimal **nerfing** gained from personal experience.

* NeRF trains best with 50 to 150 images
* Testing views should not deviate too much from training views
* Scene movement, motion blur or blurring artefacts can degrade the reconstruction quality
* The captured scene should be at least one Blender unit away from the camera
* Keep `AABB` as tight as possible to the scene scale, higher values will slow down training
* If the reconstruction quality appears blurry, start by adjusting `AABB` while keeping it a power of 2
* Avoid adjusting the camera focal lengths during the animation, the vanilla NeRF methods do not support multiple focal lengths
* Avoid extreme focal lengths, values between 30 mm and 70 mm work well in practice
* A `Vertical` camera sensor fit sometimes leads to distorted NeRF volumes, avoid it if possible


## How to NeRF

If you have access to an NVIDIA GPU, you might want to install [Instant NGP](https://github.com/NVlabs/instant-ngp#installation) on your own device for an optimal user experience, by following the instructions provided on their repository. Otherwise, you can run NeRF in a COLAB notebook on Google GPUs for free with a Google account.

Open this [COLAB notebook](https://colab.research.google.com/drive/1dQInHx0Eg5LZUpnhEfoHDP77bCMwAPab?usp=sharing) (also downloadable [here](https://gist.github.com/maximeraafat/122a63c81affd6d574c67d187b82b0b0)) and follow the instructions.


## Remarks

This add-on is being developed as a fun side project over the course of multiple months and versions of Blender, mainly on macOS. If you encounter any issues with the plugin functionalities, feel free to open a GitHub issue with a clear description of the problem, which **BlenderNeRF** version the issues have been experienced with, and any further information if relevant.

### Real World Data

While this extension is intended for synthetic datasets creation, existing tools for importing motion tracking data from real world cameras are available. One such example is **[Tracky](https://github.com/Shopify/tracky)** by **Shopify**, an open source iOS app and an adjacent Blender plugin recording motion tracking data from an ARKit session on iPhone. Keep in mind however that tracking data can be subject to drifts and inaccuracies, which might affect the resulting NeRF reconstruction quality.


## Citation

If you find this repository useful in your research, please consider citing **BlenderNeRF** using the dedicated GitHub button above. If you made use of this extension for your artistic projects, feel free to share some of your work using the `#blendernerf` hashtag on social media! :)
