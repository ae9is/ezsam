# Developers

## Development

Development is on Python 3.11. To easily switch between versions of python, consider setting up [pyenv](https://github.com/pyenv/pyenv).

This project uses [pdm](https://github.com/pdm-project/pdm) for package management with dependency resolution.

Example installation:

```bash
sudo apt install ffmpeg imagemagick
pip install pipx
pipx install pdm
git clone https://github.com/ae9is/ezsam.git
cd ezsam
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

### Operating system

Some dependencies like [pytorch](https://pytorch.org/get-started/locally/) install [differently depending on your operating system](https://discuss.pytorch.org/t/181787). 

Currently, the project just installs the default `pytorch` packages for your system on [PyPI](https://pypi.org/project/torch/). System specific dependencies are excluded from the project's lock file (list of frozen dependencies for reproducible installs).

This means Mac and Windows will end up with CPU-targeted versions of pytorch by default, and Linux users will end up with a CUDA 12.1 version of pytorch. The CPU versions of pytorch don't require an NVIDIA GPU, and the dependencies (and built executable) are much smaller, but run much slower.

If you're able to, it's highly recommended that you install a CUDA-enabled version of pytorch following the [installation matrix here](https://pytorch.org/get-started/locally/).

I.e. on Windows something like (updating version numbers as needed):
```bash
# from github project folder
source .venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
# or
pdm add https://download.pytorch.org/whl/cu121/torch-2.2.1%2Bcu121-cp311-cp311-win_amd64.whl
pdm add https://download.pytorch.org/whl/cu121/torchvision-0.17.1%2Bcu121-cp311-cp311-win_amd64.whl

```

## Releases

Release executables of the GUI are generated using [Nuitka](https://nuitka.net/).

### Standalone vs One-file

In Nuitka, a standalone release refers to a single standalone distributable folder which is then zipped up and delivered to the user to unpack.

A one-file release, which also generates a standalone distributable folder, takes the further step of bundling everything up into one executable file.

Standalone releases are larger when installed (i.e. unpacked) but start much faster. The one-file executable has to extract itself prior to running, which takes some time given the size of the ezsam machine learning library dependencies.

### Local build

Install the python requirements for making the releases:
```bash
pdm install -dG make
```

For [Nuitka](https://nuitka.net/doc/user-manual.html) requirements on Linux:
```bash
sudo apt install gcc ccache patchelf
```

See the Nuitka user manual for requirements on other platforms.

Then, the run script (which calls a bash script) to make the release is:
```bash
pdm make-nuitka
```

!!! note
    You can only generate an executable for the architecture and operating system you're running! I.e. Linux/Windows, arm64/x86_64.

### Cloud build

Multi-platform builds are setup with the GitHub workflow [make.yml](https://github.com/ae9is/ezsam/blob/main/.github/workflows/make.yml), which is manually triggered.

!!! warning
    It's recommended to build a small test program first like [tests/nuitka-test-simple.py](https://github.com/ae9is/ezsam/blob/main/tests/nuitka-test-simple.py) to make sure the workflow is working correctly. The full ezsam executable build is relatively large and takes a couple hours to build.

###
