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

## Releases

Release executables of the GUI are generated using [Nuitka](https://nuitka.net/).

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
    It's recommended to build a small test program first like [tests/nuitka-test-simple.py](https://github.com/ae9is/ezsam/blob/main/tests/nuitka-test-simple.py) to make sure the workflow is working correctly. The full ezsam executable build is relatively large and may take an hour or so to build.

###
