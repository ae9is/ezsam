# Installation

## Requirements

  - Python 3.9 - 3.11 only :material-information-outline:{ title='Python 3.12+ is not yet supported in pytorch' }
  - [FFmpeg](https://ffmpeg.org/) :material-information-outline:{ title='Only needed for video output' }
  - [ImageMagick](https://imagemagick.org/) :material-information-outline:{ title='Only needed for GIF output' }
  - *(Recommended)* Ubuntu 22.04 :material-information-outline:{ title='Development' } or Windows 10 :material-information-outline:{ title='Testing' }

## Quick start

```bash
pip install ezsam
sudo apt install ffmpeg imagemagick
ezsam --help
ezsam-gui
```

## Standard installation

```bash
pip install ezsam
```

For video output, you need to install [FFmpeg](https://ffmpeg.org/) and have it available on your `$PATH` as `ffmpeg` for 
all the encoding options except GIF.

GIF output requires [ImageMagick](https://imagemagick.org/); `convert` must be available on your `$PATH`.

```bash
# For apt-based Linuxes like Ubuntu, Debian...
sudo apt install ffmpeg imagemagick
```

If you're having trouble, see [Troubleshooting](#troubleshooting).

## Binary installation

The gui app (only) has a compiled executable release.

1. Still install FFmpeg and/or ImageMagick as in [Standard installation](install.md#standard-installation)
1. (Optional) [See here](develop.md#standalone-vs-one-file) about "standalone" vs "one-file" releases
1. [Download a release](https://github.com/ae9is/ezsam/releases)
1. Extract anywhere and run

!!! warning
    On Windows, you might have to fix the executable's permissions to allow it to run:

    1. Right click release folder or onefile executable &rarr; Properties &rarr; Security &rarr; Advanced
    1. Check "Replace all child object permissions...", if it's the release folder
    1. Select first entry "Deny Everyone Traverse folder & execute" &rarr; Remove this *Deny* permission

## Troubleshooting

### General

Thanks to pytorch, and the [general state](https://xkcd.com/927/) of [python](https://xkcd.com/1987/) package [management](https://packaging.python.org/), you might have run into installation issues.

Here's some pointers to try and help:

- Setup and use a dedicated version of python that's not your system python, using for example [pyenv](https://github.com/pyenv/pyenv)
- Use [pipx](https://pypi.org/project/pipx) to install in a separate environment: `pipx install ezsam`
- Try a [Development](develop.md#development) install, which uses locked dependencies in a virtual environment by default

If you really want to get things working:

- See if you can run similar tools: [rembg](https://github.com/danielgatis/rembg), [Segment Anything](https://github.com/facebookresearch/segment-anything), [Grounded Segment Anything](https://github.com/IDEA-Research/Grounded-Segment-Anything)
- Check the project's [Issues](https://github.com/ae9is/ezsam/issues)
- Use a CUDA 12.1 capable GPU with [NVIDIA's official drivers](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network) and set `$CUDA_HOME`{ title='i.e. /usr/local/cuda' } :material-information-outline:{ title='The machine learning projects this tool relies on are usually developed primarily for CUDA' }
- Try running the project from an Ubuntu 22.04 install or docker image

### Windows

Just in case it helps.... Here's a list of potential issues Windows 10 users might run into trying to install Python and `ezsam` from scratch, and one example (non-exhaustive) solution for each:

1. Installer from `python.org` can't be executed, even as Administrator. You've already checksummed the installer and checked its permissions.
    - Workaround: Install [Python 3.11 from the Microsoft Store](https://apps.microsoft.com/detail/9NRWMJP3717K)
1. Microsoft Store Python 3.11 can't create virtual environment (using `python -m venv .venv`)
    - Workaround: Don't create virtual environment
1. Installation (i.e. `pip install ezsam`) fails without support for long paths
    - Workaround: [https://pip.pypa.io/warnings/enable-long-paths](https://pip.pypa.io/warnings/enable-long-paths)
1. After installation, `ezsam` is not on the system PATH
    - Workaround: Add Microsoft Store python's scripts folder to your user PATH:
        1. Search bar &rarr; `Edit the system environment variables`
        2. Click `Environment Variables`
        3. User variables for `<username>` &rarr; Select and edit Path
        4. Add new variable, for example (replacing with your user AppData install location): 
        `C:\Users\<username>\AppData\Local\Packages\ PythonSoftwareFoundation.Python.3.11_xxxxxxx\LocalCache\local-packages\Python311\Scripts`

Your mileage may vary. Good luck!

###