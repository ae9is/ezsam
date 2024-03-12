#!/bin/bash
name="${1}"
version="${2}"
if [ -z "${version}" ]; then
  version="0.0.0"
fi
venv_packages=".venv/lib/python3.11/site-packages"
assets="src/${name}/gui/assets"
theme="${assets}/theme.json"
entrypoint="src/${name}/gui/app.py"
echo "Creating ${name}-${version} at `date` ..."
pyinstaller --name "${name}" \
  --windowed \
  --onefile \
  --paths "${venv_packages}" \
  --add-data="${theme}:${assets}" \
  --debug=imports \
  "${entrypoint}"
cd dist
archive="${name}-${version}.7z"
echo "Creating ${archive} at `date` ..."
# 7z compression required due to heavyweight size of ML libraries and GitHub 2GB limit on release files.
7z a "${archive}" "${name}"
sha256sum "${archive}" > "${archive}.sha256"
cd ..
echo "Finished creating ${name}-${version} at `date`"
