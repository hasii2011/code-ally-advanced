#!/opt/homebrew/bin/bash

# Note the above requires that brew be installed for OS
#

# Resizes the original images my needed sizes;
# The images here are copies fo the contracted ones.  Those
# are safely stowed away in a digital safe !!!
#
if command -v magick convert >/dev/null 2>&1; then
    echo "Resizing proceeding"
else
    echo "magick binary could not be found"
    exit 1
fi
export EXTRA_LARGE_ICONS='64x64'
export LARGE_ICONS='32x32'
export MEDIUM_ICONS='24x24'
export SMALL_ICONS='16x16'

mkdir -v ${EXTRA_LARGE_ICONS}
mkdir -v ${LARGE_ICONS}
mkdir -v ${MEDIUM_ICONS}
mkdir -v ${SMALL_ICONS}

export SOURCE_DIRECTORY='./sourceImages'

echo "Create ${EXTRA_LARGE_ICONS} icons"
magick mogrify -path ${EXTRA_LARGE_ICONS} -resize ${EXTRA_LARGE_ICONS} ${SOURCE_DIRECTORY}/*.png

echo "Create ${LARGE_ICONS} icons"
magick mogrify -path ${LARGE_ICONS} -resize ${LARGE_ICONS} ${SOURCE_DIRECTORY}/*.png

echo "Create ${MEDIUM_ICONS} icons"
magick mogrify -path ${MEDIUM_ICONS} -resize ${MEDIUM_ICONS} ${SOURCE_DIRECTORY}/*.png

echo "Create ${SMALL_ICONS} icons"
magick mogrify -path ${SMALL_ICONS} -resize ${SMALL_ICONS} ${SOURCE_DIRECTORY}/*.png

echo "Done !!!"