# ezsam (easy segment anything model)

A tool to segment images and video via text prompts.

Input images and videos, describe the subjects or objects you want to keep, and output new images and videos with the background removed.

## Why?

Meta's [Segment Anything](https://github.com/facebookresearch/segment-anything) is a powerful tool for separating parts of images,
but requires coordinate prompts&mdash;either bounding boxes or points.
And manual prompt generation is tedious for large collections of still images or video.

In constrast, text-based prompts describing the object(s) in the foreground to segment can be constant.
Inspired by [Grounded-Segment-Anything](https://github.com/IDEA-Research/Grounded-Segment-Anything),
this project tries to package a simpler to use tool.

If you're not interested in text-based prompts with Segment Anything, 
check out [rembg](https://github.com/danielgatis/rembg).

## How does it work?

The foreground is selected using text prompts to [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO) to detect objects.
Image segments are generated using [Segment Anything](https://github.com/facebookresearch/segment-anything) 
or [Segment Anything HQ (SAM-HQ)](https://github.com/SysCV/SAM-HQ).

#####

[Get started](install.md){ .md-button .md-button--primary .float-right }
[Learn more](usage.md){ .md-button .float-right .mr-2 }

###