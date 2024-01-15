# ezsam (easy segment anything model)

A pipeline to extract foreground from images or video via text prompts.

## Why?

Meta's Segment Anything is a powerful tool for separating parts of images,
but requires coordinate prompts&mdash;either bounding boxes or points.
Manual prompt generation is tedious for large collection of still images or video.
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

TODO

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

For the best results use the biggest model your GPU has memory for.
From best (slowest) to worst (fastest): ViT-H > ViT-L > ViT-B > ViT-tiny (SAM-HQ only)

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
