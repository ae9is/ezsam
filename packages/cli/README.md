# ezsam (easy segment anything model)

A pipeline to extract foreground from images or video via text prompts.

## Why?

Meta's Segment Anything is a powerful tool for separating parts of images,
but requires coordinate prompts&mdash;either bounding boxes or points.
Manual prompt generation is tedious for large collections of still images or video.
In constrast, text-based prompts describing the object(s) in the foreground to segment can be constant.
Inspired by [Grounded-Segment-Anything](https://github.com/IDEA-Research/Grounded-Segment-Anything),
this project tries to package a simpler to use tool.

If you're not interested in text-based prompts with Segment Anything, 
check out [rembg](https://github.com/danielgatis/rembg).

## How does it work?

The foreground is selected using text prompts to [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO) to detect objects.
Image segments are generated using [Segment Anythinug](https://github.com/facebookresearch/segment-anything) 
or [Segment Anything HQ (SAM-HQ)](https://github.com/SysCV/SAM-HQ).

## Installation 

```bash
pip install ezsam
```

For video output, you need to install FFmpeg and have it available on your $PATH as `ffmpeg` for 
all the encoding options except GIF. GIF output requires Imagemagick; `convert` must be available on your $PATH.

```bash
# Examples will be given for apt-based Linuxes like Ubuntu, Debian...
apt install ffmpeg imagemagick
```

For a development install, see [Development](#development).

## Usage

```bash
ezsam --help
```

## Examples

Example images are sourced from [rembg](https://github.com/danielgatis/rembg/tree/main/examples) for easy comparison.

Process images extracting foreground specified by prompt to `examples/animal*.out.png`.
(For extractions, which require adding an alpha channel, the output image format is always `png`.)

```bash
ezsam examples/animal*.jpg -p animal -o examples
```

Multiple objects can be selected as the foreground. The output image `./car-1.out.png` contains the car and the person.

```bash
ezsam examples/car-1.jpg -p car, person
```

Use debug mode to fine tune or troubleshoot prompts. This writes output with foreground mask and object detections
annotated over the original image file. Here we write out to `test/car-3.debug.jpg`.
(Note the original image format `jpg` is preserved in debug mode!)

```bash
ezsam examples/car-3.jpg -p white car -o test -s .debug --debug
```

The object detection box threshold parameter can be used to fine tune objects for selection.

```bash
ezsam examples/car-3.jpg -p white car -o test --bmin 0.45
```

Writing prompts with specificity can also help.

```bash
ezsam examples/anime-girl-2.jpg -o examples -s .debug -p girl, phone, bag, railway crossing sign post --debug
```

## Models

The tool uses [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO) for object detection.

To perform image segmentation, you can pick SAM or SAM-HQ:
* [Segment Anything](https://github.com/facebookresearch/segment-anything) 
* [Segment Anything HQ (SAM-HQ)](https://github.com/SysCV/SAM-HQ)

For the best results use the biggest model your GPU has memory for. ViT = Vision Transformer, the model type. From best/slowest to worst/fastest: ViT-H > ViT-L > ViT-B > ViT-tiny.

Note: ViT-tiny is for SAM-HQ only, you must use the `--hq` flag.

## Development

This project uses [pdm](https://github.com/pdm-project/pdm) for package management. Example installation:

```bash
pip install pipx
pipx install pdm
git clone https://github.com/ae9is/ezsam.git
cd ezsam/packages/cli
pdm install
pdm start
```

Pre-commit is used for some commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## GPU memory troubleshooting

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

Note: nvidia-smi is in the nvidia-utils package of [NVIDIA's CUDA repo for Ubuntu](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network).
