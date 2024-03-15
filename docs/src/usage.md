# Usage

## GUI app
A simple graphical user interface for the command line `ezsam` tool can be started via:

```bash
ezsam-gui
```

!!! note
    The gui can only process a single image or video file at a time, and the output is written to `<current_directory>/<input_filename>.out.<output_extension>`

## Options
The command-line app `ezsam` contains more options than the gui:

```bash
ezsam --help
```

## Examples

The [example images](https://github.com/ae9is/ezsam/tree/main/examples) are sourced from [rembg](https://github.com/danielgatis/rembg/tree/main/examples) for easy comparison.

### Simple image extraction
Process images extracting foreground specified by prompt to `examples/animal*.out.png`.

```bash
ezsam examples/animal*.jpg -p animal -o examples
```

<img src="https://raw.githubusercontent.com/ae9is/ezsam/main/examples/animal-1.out.png" width=200 />
<img src="https://raw.githubusercontent.com/ae9is/ezsam/main/examples/animal-2.out.png" width=200 />

!!! note
    For image extractions, which require adding an alpha channel, the output image format is always `png`.

### Video filtering
Video files are handled automatically.

```bash
ezsam car.mkv -p car
```

!!! warning
    In order to output most of the allowed video formats, FFmpeg needs to be installed and on your `$PATH`. For GIF output, ImageMagick needs to be installed, with the `convert` command available. See [Installation](install.md).

### Multiple subjects
Multiple objects can be selected as the foreground. The output image `./car-1.out.png` contains the car and the person.

```bash
ezsam examples/car-1.jpg -p car, person
```

<img src="https://raw.githubusercontent.com/ae9is/ezsam/main/examples/car-1.out.png" width=400 />

### Debug mode
Use debug mode to fine tune or troubleshoot prompts. This writes output with foreground mask and object detections
annotated over the original image file. Here we write out to `test/car-3.debug.jpg`.


```bash
ezsam examples/car-3.jpg -p white car -o test -s .debug --debug
```

<img src="https://raw.githubusercontent.com/ae9is/ezsam/main/examples/car-3.debug.jpg" width=400 />

!!! note
    Note the original image format `jpg` is preserved in debug mode!

### Object detection box tuning
The object detection box threshold parameter can be used to fine tune objects for selection.

```bash
ezsam examples/car-3.jpg -p white car -o test --bmin 0.45
```

<img src="https://raw.githubusercontent.com/ae9is/ezsam/main/examples/car-3.white.png" width=400 />

Or...

```bash
ezsam examples/food.mp4 -p turkey -o examples -s .turkey --hq -m vit_h --keep --bmin 0.46
```

<video src="https://raw.githubusercontent.com/ae9is/ezsam/main/examples/food.turkey.webm" height=400 controls>
  A whole cooked turkey flying through the void.
</video>

### Complex prompts
Writing prompts with specificity can also help.

```bash
ezsam examples/anime-girl-2.jpg -o examples -s .debug -p girl, phone, bag, railway crossing sign post --debug
```

<img src="https://raw.githubusercontent.com/ae9is/ezsam/main/examples/anime-girl-2.debug.jpg" width=400 />

!!! note
    When the GroundingDINO object detection model can't map your input prompt onto any classes for a detection box with confidence, in debug mode the generated label for that box will be "Error" instead.

### Negative prompting
Negative (inverse) prompt selections can be used to remove specific objects from selection.

```bash
ezsam examples/anime-girl-2.jpg -o examples -s .out -p train -n window
```

<img src="https://raw.githubusercontent.com/ae9is/ezsam/main/examples/anime-girl-2.out.png" width=400 />

## Models

The tool uses [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO) for object detection.

To perform image segmentation, you can pick SAM or SAM-HQ:

* [Segment Anything](https://github.com/facebookresearch/segment-anything) 
* [Segment Anything HQ (SAM-HQ)](https://github.com/SysCV/SAM-HQ)

For the best results use the biggest model your GPU has memory for. ViT = Vision Transformer, the model type. From best/slowest to worst/fastest: ViT-h(uge) > ViT-l(arge) > ViT-b(ase) > ViT-tiny.

!!! note
    ViT-tiny is for SAM-HQ only, you must use the `--hq` flag.

## Troubleshooting

### GPU memory

If you *always* get an error stating "CUDA out of memory", try using a smaller Segment Anything model (vit_tiny, vit_b) or lower resolution (or less) input.

If you only get a CUDA OOM error occasionally, or after a while, try to free up some memory by closing processes using the GPU:
```bash
# List commands using nvidia gpu
fuser -v /dev/nvidia*
```

You can also try manually getting the GPU to clear some processes:
```bash
# Clears all processes accounted so far
sudo nvidia-smi -caa
```

If you are using multiple GPUs, and so the GPU you're running CUDA on isn't driving your displays, you can also reset the GPU using:
```bash
# Trigger reset of one or more GPUs
sudo nvidia-smi -r
```

!!! note
    nvidia-smi is in the nvidia-utils package of [NVIDIA's CUDA repo for Ubuntu](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network).

### GUI

#### Job failures
On certain job failures the gui might not detect the job as ended, keeping the cursor spinning and preventing another run from being queued. A workaround is to just restart.

#### Slow to load
The one-file build takes a couple seconds to extract itself and start up, [see here](develop.md#standalone-vs-one-file).

###
