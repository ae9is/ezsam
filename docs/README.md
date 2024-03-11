# ezsam/docs

Static docs site using [Material for MkDocs](https://github.com/squidfunk/mkdocs-material)

## Install

```bash
pdm install
```

## Run

```bash
pdm start
```

## Deployment

Checkout the github action at [.github/workflows/pages.yml](/.github/workflows/pages.yml)

To manually deploy to your local Git repository's gh-pages branch:

```bash
pdm deploy-pages
```

## Development

Checkout the repos for [mkdocs-material](https://github.com/squidfunk/mkdocs-material) and [pdm](https://github.com/pdm-project/pdm) for examples (for generating versioned docs, api docs from doc strings, etc...)
