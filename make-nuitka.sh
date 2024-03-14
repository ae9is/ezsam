#!/bin/bash
# Create executable from python project using Nuitka
echo "Called make-nuitka.sh with arguments:"
for arg in "$@"
do
  echo "${arg}"
done
name="${1}"
entrypoint="${2}"
version="${3}"
dist="${4}"
assets="${5}"
description="${6}"
CI="${7}"
if [ -z "${name}" ]; then
  name="ezsam"
fi
if [ -z "${entrypoint}" ]; then
  entrypoint="src/${name}/gui/app.py"
fi
if [ -z "${version}" ]; then
  version="0.0.0"
fi
if [ -z "${dist}" ]; then
  dist="dist-nuitka"
fi
if [ -z "${assets}" ]; then
  assets="src/ezsam/gui/assets"
fi
if [ -z "${description}" ]; then
  description='ezsam is a tool to extract objects from images or video via text prompt - info at https://www.ezsam.org'
fi
tempdir="{TEMP}/ezsam"  # Should match ezsam.lib.config.EXECUTABLE_NAME
outfile="${name}"
echo "Creating ${name}-${version} at `date` ..."
python -m nuitka --enable-plugin=tk-inter --onefile --assume-yes-for-downloads --disable-console \
  --onefile-tempdir-spec="${tempdir}" \
  --include-data-dir="${assets}=${assets}" \
  --output-filename="${outfile}" \
  --product-version="${version}" \
  --file-version="${version}" \
  --file-description="${description}" \
  --output-dir="${dist}" "${entrypoint}"
# Move onefile executable to different folder and checksum
cd "${dist}"
mkdir -p "onefile"
mv "${outfile}" "onefile/${outfile}"
cd onefile
sha256sum "${outfile}" > "${outfile}.sha256"
cd ..
base=`basename ${entrypoint} .py`
outdir="${name}-${version}"
mv "${base}.dist" "${outdir}"  # outdir will be zipped up in CI automatically
if [ -z "${CI}" ]; then
  # No CI flag, running locally.
  # We have zip executable locally and want to just directly create a useful archive and checksum.
  echo "Running post-build tasks for local building at `date` ..."
  zip -r "${outdir}.zip" "${outdir}"
  sha256sum "${outdir}.zip" > "${outdir}.zip.sha256"
  # Now that we have our archive undo move to prevent future runs of Nuikta from failing
  mv "${outdir}" "${base}.dist" 
else
  # In CI, clean up build directories to save space
  echo "Running post-build tasks for CI building at `date` ..."
  rm -rf "${base}.build"
  rm -rf "${base}.onefile-build"
fi
cd ..
echo "Finished creating ${name}-${version} at `date`"
