# Blender x NeRF

**Blender x NeRF** is a Blender add-on for creating virtual datasets, leveraged by an AI to synthesize images from unseen viewpoints. The constructed datasets can directly be utilised for training and testing a *Neural Radiance Field ([NeRF](https://www.matthewtancik.com/nerf))* model, yielding AI predicted images in a matter of seconds.

This quick and user friendly tool attempts to narrow the gap between the artistic creation process and state-of-the-art research in computer graphics and vision.

<p align='center'>
  <img src='https://maximeraafat.github.io/assets/posts/donut_3/Donut3_compressed.gif' width='400'/>
  <img src='https://maximeraafat.github.io/assets/posts/donut_3/Donut3_NeRF_compressed.gif' width='400'>
  <br>
  <b>
    Left : traditional rendering with Eevee renderer
    <br>
    Right : NeRF-synthesized images
  </b>
</p>

## Motivation

Rendering is a computationally intensive process ; generating photorealistic scenes can take seconds to hours depending on the scene complexity, hardware properties and the computational resources available to the 3D software.

While obtaining renderings might be considered a straight forward process for 3D artists, obtaining the additional camera information necessary for NeRF can be discouraging, even for python familiar users or machine learning developers. This add-on aims at solving this issue, enabling artists to easily integrate AI in their creative flow while also facilitating research.


## Installation

1. Download this repository as a ZIP file
2. Open Blender (3.0.0 or above. For previous versions, see the [Upcoming](#upcoming) section)
3. In Blender, head to *Edit > Preferences > Add-ons*, and click *Install...*
4. Select the downloaded ZIP file, and activate the add-on (Object: Blender x NeRF)


## Setting

**Blender x NeRF** proposes 3 methods, which are discussed in the sub-sections below. From now on when mentioning *training* data, I will refer to the data required by NeRF to *train* (or teach) the AI model. Similarly, the *testing* data will refer to the images predicted by the AI.
When executed, each of the 3 methods generate an archived ZIP file, containing a training and testing folder. Both folders contain a `transforms_train.json` file, respectively `transforms_test.json` file, with the necessary camera information for NeRF to properly train and test on images.

### SOF : Subset of Frames

SOF renders every N frames from a camera animation, and uses those as training data for NeRF. Testing will be executed on all animation frames, that is, both training frames and the remaining ones.

### TTC : Train and Test Cameras

TTC registers training and testing data from two separate user defined cameras. NeRF will then train on all animation frames rendered with the training camera, and predict all frames seen by the testing camera.

### COS : Camera on Sphere (upcoming)

COS renders frames from random views on a sphere while looking at its center, with user defined radius and center location. Those frames will then serve as training data for NeRF. Testing frames are still to be decided (perhaps a predefined spherical trajectory, or a user defined camera path).


## How to use the add-on

The add-on properties panel is available under `3D View > N panel > BlenderNeRF` (The N panel is accessible under the 3D viewport when pressing *N*). All 3 methods (**SOF**, **TTC** and **COS**) share a common tab called `Blender x NeRF shared UI`, which appears per default at the top of add-on panel. The shared tab contains the below listed controllable properties.

* `Train` (activated by default) : whether to register training data (camera information + renderings)
* `Test` (activated by default) : whether to register testing data (camera information only)
* `AABB` (by default set to *4*) : aabb scale parameter as described in Instant NGP (more details below)
* `Render Frames` (activated by default) : whether to render the frames
* `Save Path` (empty by default) : path to the output directory in which the dataset will be stored


`AABB` is restricted to be an integer power of 2, and defines the side length of the bounding box volume in which NeRF will trace rays. The property was introduced in *NVIDIA's [Instant NGP](https://github.com/NVlabs/instant-ngp)* version of NeRF, which is currently the only supported version. Future releases of this add-on might support different versions.

Notice that each method has a `Name` property (by default set to *dataset*), which corresponds to the name of the dataset and ZIP file that will be created for the respective method. Each method can set a different dataset name, without affecting the `Name` properties of the other methods. Please avoid using unsupported characters (such as spaces, #, or /), as those characters will all be replaced by an underscore.

Below are described the properties specific to each method (the `Name` property is left out, as discussed above).

### How to SOF

* `Frame Step` (by default set to *3*) : N (as defined in the [Setting](#setting)) = frequency at which we render the frames for training
* `Camera` (always set to the activate camera) : camera used for registering training and testing data
* `PLAY SOF` : play the *Subset of Frames* method

### How to TTC

* `Train Cam` (empty by default) : camera used for registering the training data
* `Test Cam` (empty by default) : camera used for registering the testing data
* `PLAY TTC` : play the *Train and Test Cameras* method

### How to COS (upcoming)


## Tips for optimal results

As already specified in the previous section, the add-on currently only supports *NVIDIA's [Instant NGP](https://github.com/NVlabs/instant-ngp)* version of NeRF. Feel free to visit their repository for detailed instructions on how to obtain realistic predicted images, or technicalities on their lightning fast NeRF implementation. Below are some quick tips for optimal NeRF training and testing.

* NeRF trains best with 50 to 150 images
* Testing views should not deviate to much from training views (applies especially to TTC)
* Scene movement, motion blur or blurring artefacts, degrade the predicted quality. Avoid them if possible.
* The object should be at least one Blender unit away from the camera : the closer the object is to the camera, the lower you should set `AABB`. Keep it as low as possible, as higher values will increase the training time
* If the predicted quality seems blurry, start with adjusting `AABB`, while keeping it a power of 2
* Do not adjust the camera focal length during the animation, as Instant NGP only supports a single focal length as input to NeRF

Unfortunately, NeRF is not capable of predicting transparent pixels for RGBA images : the method predicts for each pixel a color and a density. Transparency (e.g., under the form of a transparent background) results in invalid density values, causing the transparent background in your training images to be replaced by a monochrome color.


## How to run NeRF

If you possess an NVIDIA GPU, you might want to install [Instant NGP](https://github.com/NVlabs/instant-ngp) on your own device for an optimal user experience with a GUI by following the instructions provided in their GitHub repository. Otherwise, you can run NeRF in a COLAB notebook on Google GPUs for free (all you need is a Google account).

Open this [COLAB notebook](https://colab.research.google.com/drive/1CtF_0FgwzCZMYQzGXbye2iVS1ZLlq9Tw?usp=sharing) (also downloadable [here](https://gist.github.com/maximeraafat/122a63c81affd6d574c67d187b82b0b0)) and follow the instructions.


## Upcoming
* Support for previous blender versions
* If frames have already been rendered, enable the possibility to copy the already rendered frames to the dataset instead of rendering them again
* COS method (add-on release version 3.0)
* Support for other NeRF implementations, for example [Torch NGP](https://github.com/ashawkey/torch-ngp)?
* Once all methods are released : publish simple explanatory tutorial video
