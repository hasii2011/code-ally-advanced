#!/opt/homebrew/bin/bash

# Note the above requires that brew be installed for OS
#

export EXTRA_LARGE_ICONS='64x64'
export LARGE_ICONS='32x32'
export MEDIUM_ICONS='24x24'
export SMALL_ICONS='16x16'

export OUTPUT_DIR="../../src/codeallyadvanced/resources/umldiagrammer/"
export EMBEDDED_FILE64="${OUTPUT_DIR}Embedded64.py"
export EMBEDDED_FILE32="${OUTPUT_DIR}Embedded32.py"
export EMBEDDED_FILE24="${OUTPUT_DIR}Embedded24.py"
export EMBEDDED_FILE16="${OUTPUT_DIR}Embedded16.py"

#img2py  -n Actor       -a  -i ${EXTRA_LARGE_ICONS}/Actor.png          ${EMBEDDED_FILE64}
#img2py  -n Aggregation -a  -i ${EXTRA_LARGE_ICONS}/Aggregation.png    ${EMBEDDED_FILE64}


for imageFile in ${EXTRA_LARGE_ICONS}/*.png
do
  # echo "$imageFile"
  justName="$(basename $imageFile .png)"
  # echo "$justName"
  img2py  -n ${justName} -a  -i $imageFile      ${EMBEDDED_FILE64}
done

for imageFile in ${LARGE_ICONS}/*.png
do
  # echo "$imageFile"
  justName="$(basename $imageFile .png)"
  # echo "$justName"
  img2py  -n ${justName} -a  -i $imageFile      ${EMBEDDED_FILE32}
done

for imageFile in ${MEDIUM_ICONS}/*.png
do
  # echo "$imageFile"
  justName="$(basename $imageFile .png)"
  # echo "$justName"
  img2py  -n ${justName} -a  -i $imageFile      ${EMBEDDED_FILE24}
done

for imageFile in ${SMALL_ICONS}/*.png
do
  # echo "$imageFile"
  justName="$(basename $imageFile .png)"
  # echo "$justName"
  img2py  -n ${justName} -a  -i $imageFile      ${EMBEDDED_FILE16}
done
