# Blender x NeRF

**Blender x NeRF** is a Blender add-on for creating virtual datasets, leveraged by an AI to synthesize images from unseen viewpoints. The constructed datasets can directly be utilised for training and testing a *Neural Radiance Field ([NeRF](https://www.matthewtancik.com/nerf))* model, yielding AI predicted images in a matter of seconds.

This quick and user friendly tool attempts to narrow the gap between the artistic creation process and state-of-the-art research in computer graphics and vision.


## Motivation

Rendering is a computationally intensive process ; generarting photorealistic scenes can take seconds to hours depending on the scene complexity, hardware properties and the computational resources available to the 3D software.

While obtaining renderings might be considered a straight forward process for 3D artists, obtaining the additional camera information necessary for NeRF can be discouraging, even for python familiar users or machine learning developers. This add-on aims at solving this issue, enabling artists to easily integrate AI in their creative flow while also faciliating research.

SHOW GIF RESULTS


## Installation

1. Download this repository as a ZIP file
2. Open Blender (3.0.0 or above. For previous versions, see the [Upcoming](#upcoming) section)
3. In Blender, head to *Edit > Preferences > Add-ons*, and click *Install...*
4. Select the downloaded ZIP file, and activate the add-on (Object: Blender x NeRF)


## Setting

**Blender x NeRF** proposes 3 settings, which are discussed in the sub-sections below. From now on when mentioning *training* data, I will refer to the data required by NeRF to *train* (or teach) the AI model. Similarly, the *testing* data will refer to the images predicted by the AI.
When executed, each of the 3 settings generate an archived ZIP file, contaning a training and testing folder. Both folders contain a `transforms_train.json` file, respectively `transforms_test.json` file, with the necessary camera information for NeRF to properly train and test on images.

### SOF : Subset of Frames

SOF renders every N frames from an animation, and uses those as training data for NeRF. Testing will be executed on all animation frames, that is, both training frames and the remaining ones.

### TTC : Train and Test Cameras (upcoming)

TTC registers training and testing data from two separate user defined cameras. NeRF will then train on all animation frames rendered with the training camera, and predict all frames seen by the testing camera.

### COS : Camera on Sphere (upcoming)

COS renders frames from random views on a sphere while looking at its center, with user defined radius and center location. Those frames will then serve as training data for NeRF. Testing frames are still to be decided (perhaps a predefined spherical trajectory, or a user defined camera path).


## How to use the add-on

The add-on properties panel is available under `3D View > N panel > Blender x NeRF` (The N panel is accessible under the 3D viewport when pressing *N*). All 3 categories (**SOF**, **TTC** and **COS**) have a similar user interfance with shared properties (accessible with clickable buttons or sliders) discussed below.

* `Train` (activated by default) : whether to register training data (camera information + renderings)
* `Test` (activated by default) : whether to register testing data (camera information only)
* `AABB` (by default set to *4*) : aabb scale parameter as described in Instant NGP (more details below)
* `Render Frames` (activated by default) : whether to render the frames
* `Save Path` (empty by default) : path to the output directory in which the dataset will be stored
* `Name` (by default set to *dataset*) : name of the dataset and ZIP file that will be created

The `AABB` property is only available for *NVIDIA's [Instant NGP](https://github.com/NVlabs/instant-ngp)* version of NeRF, which currently is the only supported version. Future releases of this add-on might support different versions.

Please avoid using unsupported characters (such as spaces, #, or /) for `Name`, as those characters will all be replaced by an underscore.

Below, you can find properties specific to each category.

### How to SOF

* `Camera` (always set to the activated camera) : camera used for registering training and testing data
* `Frame Step` (by default set to *3*) : N (as defined in the [Setting](#setting)) = frequency at which we render the frames for training
* `PLAY SOF` : play the *Subset of Frames* add-on

### How to TTC (upcoming)

### How to COS (upcoming)


## Tips for optimal results

As already specified in the previous section, the add-on currently only supports *NVIDIA's [Instant NGP](https://github.com/NVlabs/instant-ngp)* version of NeRF. Feel free to visit their repository for detailled instructions on how to obtain realistic predicted images, or technicalities on their lightning fast NeRF implementation. Below you can find some quick tips for optimal training and testing of NeRF.

* NeRF trains best with 50 to 150 images
* Testing views should not deviate to much from training views (applies especially to TTC)
* Scene movement, motion blur or blurring artefacts, and scene background degrade the predicted quality. Avoid them if possible.
* The object should be at least one Blender unit away from the camera : the closer the object is to the camera, the lower you can set `AABB`. A lower value will accelerate the training
* If the predicted quality seems blurry, start with changing `AABB` (to larger or lower values). `AABB` has to be a power of 2!


## How to run NeRF

Now that you finally created the necessary data to run NeRF, it's finally time to feed the elephant in the room. If you possess an NVIDIA GPU, you might want to install [Instant NGP](https://github.com/NVlabs/instant-ngp) on your own device for an optimal user experience with a GUI, by following the instructions provided in their GitHub repository. Otherwise, you can run NeRF in a COLAB notebook on Google GPUs for free (all you need is a Google account).

Open this [COLAB notebook](https://drive.google.com/file/d/1Fbd985Bfj7BrTgriwmOKkuh-J40JjYHK/view?usp=sharing) (also downloadable [here](https://gist.github.com/maximeraafat/122a63c81affd6d574c67d187b82b0b0))and follow the instructions.

Unfortunately, NeRF is not capable of predicting images with a transparent background : NeRF predicts for each pixel a color and a density. A transparent background would result in an invalid density value, therefore explaining the monochrome background color. If you want to remove the background, you can apply a simple Blender mask to your predicted images, to remove pixel values above or below a certain color threshold.

## Upcoming
* For SOF and TOC, if frames have already been rendered, enable the possibilty to copy the already rendered frames to the dataset instead of rendering them again
* Support for previous blender versions
* TOC setting (add-on release version 2.0)
* COS setting (add-on release version 3.0)
* Support for other NeRF implementations, for example [Torch NGP](https://github.com/ashawkey/torch-ngp)?
<!--
* Extend add-on to Blender Market?
* Update testing.py to fit current version
-->
