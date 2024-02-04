# Usage

## Options

```bash
ezsam --help
```

## Examples

The [example images](https://github.com/ae9is/ezsam/tree/main/packages/cli/examples) are sourced from [rembg](https://github.com/danielgatis/rembg/tree/main/examples) for easy comparison.

### Simple image extraction
Process images extracting foreground specified by prompt to `examples/animal*.out.png`.

```bash
ezsam examples/animal*.jpg -p animal -o examples
```

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

### Debug mode
Use debug mode to fine tune or troubleshoot prompts. This writes output with foreground mask and object detections
annotated over the original image file. Here we write out to `test/car-3.debug.jpg`.


```bash
ezsam examples/car-3.jpg -p white car -o test -s .debug --debug
```

!!! note
    Note the original image format `jpg` is preserved in debug mode!

### Object detection box tuning
The object detection box threshold parameter can be used to fine tune objects for selection.

```bash
ezsam examples/car-3.jpg -p white car -o test --bmin 0.45
```

### Complex prompts
Writing prompts with specificity can also help.

```bash
ezsam examples/anime-girl-2.jpg -o examples -s .debug -p girl, phone, bag, railway crossing sign post --debug
```

### Negative prompting
Negative (inverse) prompt selections can be used to remove specific objects from selection.

```bash
ezsam examples/anime-girl-2.jpg -o examples -s .out -p train -n window
```

## Models

The tool uses [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO) for object detection.

To perform image segmentation, you can pick SAM or SAM-HQ:

* [Segment Anything](https://github.com/facebookresearch/segment-anything) 
* [Segment Anything HQ (SAM-HQ)](https://github.com/SysCV/SAM-HQ)

For the best results use the biggest model your GPU has memory for. ViT = Vision Transformer, the model type. From best/slowest to worst/fastest: ViT-H > ViT-L > ViT-B > ViT-tiny.

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

###
