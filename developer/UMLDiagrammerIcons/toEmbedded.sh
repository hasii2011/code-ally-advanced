#!/opt/homebrew/bin/bash

# Note the above requires that brew be installed for OSX
# Assumes the XX_ICONS directory were created by the resize.sh script
#

export EXTRA_LARGE_ICONS='64x64'
export LARGE_ICONS='32x32'
export MEDIUM_ICONS='24x24'
export SMALL_ICONS='16x16'

if [ -z "$1" ]; then
  echo "Usage: $0 <OUTPUT_DIR>"
  exit 1
fi

export OUTPUT_DIR="$1"
export BASE_DIR="../../src/codeallyadvanced/resources"
export FULL_DIR="${BASE_DIR}/${OUTPUT_DIR}"

if [ ! -d "$FULL_DIR" ]; then
  read -p "Directory $FULL_DIR does not exist. Create it? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p "$FULL_DIR"
  else
    echo "Directory creation cancelled. Exiting."
    exit 1
  fi
fi

export EMBEDDED_FILE64="${FULL_DIR}/Embedded64.py"
export EMBEDDED_FILE32="${FULL_DIR}/Embedded32.py"
export EMBEDDED_FILE24="${FULL_DIR}/Embedded24.py"
export EMBEDDED_FILE16="${FULL_DIR}/Embedded16.py"

echo "from wx.lib.embeddedimage import PyEmbeddedImage" > "${EMBEDDED_FILE64}"
echo "from wx.lib.embeddedimage import PyEmbeddedImage" > "${EMBEDDED_FILE32}"
echo "from wx.lib.embeddedimage import PyEmbeddedImage" > "${EMBEDDED_FILE24}"
echo "from wx.lib.embeddedimage import PyEmbeddedImage" > "${EMBEDDED_FILE16}"


for imageFile in ${EXTRA_LARGE_ICONS}/*.png
do
  justName="$(basename $imageFile .png)"
  img2py  -n ${justName} -a  -i $imageFile      ${EMBEDDED_FILE64}
done

for imageFile in ${LARGE_ICONS}/*.png
do
  justName="$(basename $imageFile .png)"
  img2py  -n ${justName} -a  -i $imageFile      ${EMBEDDED_FILE32}
done

for imageFile in ${MEDIUM_ICONS}/*.png
do
  justName="$(basename $imageFile .png)"
  img2py  -n ${justName} -a  -i $imageFile      ${EMBEDDED_FILE24}
done

for imageFile in ${SMALL_ICONS}/*.png
do
  justName="$(basename $imageFile .png)"
  img2py  -n ${justName} -a  -i $imageFile      ${EMBEDDED_FILE16}
done
