#!/bin/bash
# Create executable from python project using Nuitka
name="${1}"
entrypoint="${2}"
version="${3}"
if [ -z "${name}" ]; then
  name="ezsam"
fi
if [ -z "${entrypoint}" ]; then
  entrypoint="src/${name}/gui/app.py"
fi
if [ -z "${version}" ]; then
  version="0.0.0"
fi
assets="src/ezsam/gui/assets"
description='ezsam is a tool to extract objects from images or video via text prompt - info at https://www.ezsam.org'
dist="dist-nuitka"
tempdir="{TEMP}/ezsam"
outfile="${name}-${version}.bin"
echo "Creating ${name}-${version} at `date` ..."
python -m nuitka --enable-plugin=tk-inter --onefile \
  --onefile-tempdir-spec="${tempdir}" \
  --include-data-dir="${assets}=${assets}" \
  --output-filename="${outfile}" \
  --product-version="${version}" \
  --file-version="${version}" \
  --file-description="${description}" \
  --output-dir="${dist}" "${entrypoint}"
cd dist
# Note: Nuitka default compression almost as good as 7z
sha256sum "${outfile}" > "${outfile}.sha256"
cd ..
echo "Finished creating ${name}-${version} at `date`"
