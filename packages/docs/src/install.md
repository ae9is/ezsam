# Installation

## Requirements

  - Python 3.9 - 3.11 only :material-information-outline:{ title='Python 3.12 is not yet supported in pytorch' }
  - [FFmpeg](https://ffmpeg.org/) :material-information-outline:{ title='Only for video output' }
  - [ImageMagick](https://imagemagick.org/) :material-information-outline:{ title='Only for GIF output' }

## Quick start

```bash
pip install ezsam
sudo apt install ffmpeg imagemagick
ezsam --help
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

## Development

Development is on Python 3.11. To easily switch between versions of python, consider setting up [pyenv](https://github.com/pyenv/pyenv).

This project uses [pdm](https://github.com/pdm-project/pdm) for package management with dependency resolution.

Example installation:

```bash
sudo apt install ffmpeg imagemagick
pip install pipx
pipx install pdm
git clone https://github.com/ae9is/ezsam.git
cd ezsam/packages/cli
pdm install
pdm start
```

!!! note
    [pipx](https://pypi.org/project/pipx) is used to install `pdm` in a separate environment. This is important for a dependency management program, so that it doesn't break itself! But you might find `pdm` works just fine via regular `pip` install.

Some environment variables in `.env` in the project root are set using [direnv](https://direnv.net/).

Set it up, edit your `.env` file, and then in project root directory run:
```bash
direnv allow
```

Pre-commit is used for some commit hooks:
```bash
pip install pre-commit
pre-commit install
```

Some dependencies like [pytorch](https://pytorch.org/get-started/locally/) install differently depending on your operating system. Currently, the project just installs the default `pytorch` packages for your o/s on [PyPI](https://pypi.org/project/torch/) and excludes o/s specific dependencies are excluded from the project's lock file (list of frozen dependencies for reproducible installs).

## Troubleshooting

Thanks to pytorch, and the general state of python package management, you might have run into installation issues.

Here's some pointers to try and help:

- Setup and use a dedicated version of python that's not your system python, using for example [pyenv](https://github.com/pyenv/pyenv)
- Use [pipx](https://pypi.org/project/pipx) to install in a separate environment: `pipx install ezsam`
- Try a [Development](#development) install, which uses locked dependencies in a virtual environment by default

If you really want to get things working:

- See if you can run similar tools: [rembg](https://github.com/danielgatis/rembg), [Segment Anything](https://github.com/facebookresearch/segment-anything), [Grounded Segment Anything](https://github.com/IDEA-Research/Grounded-Segment-Anything)
- Check the project's [Issues](https://github.com/ae9is/ezsam/issues)
- Use a CUDA 12.1 capable GPU with [NVIDIA's official drivers](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network) and set `$CUDA_HOME`{ title='i.e. /usr/local/cuda' } :material-information-outline:{ title='The machine learning projects this tool relies on are usually developed primarily for CUDA' }
- Try running the project from an Ubuntu 22.04 install or docker image

###