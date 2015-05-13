#!/bin/bash
#
# Read the raw METBK data files for the Endurance Coastal Surface Moorings and
# create parsed datasets available in Matlab formatted .MAT files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# TODO: Convert this to accept input arguements for platform and deployment names

RAW="/home/nereus/data/Moorings/raw"
PARSED="/home/nereus/data/Moorings/parsed"

# CE02SHSM
OUT="$PARSED/ce02shsm/D00001/superv/dcl11"
for raw in $RAW/ce02shsm/D00001/cg_data/dcl11/superv/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_superv_dcl.py -i $raw -o $OUT/${FILE%.log}.mat
done
OUT="$PARSED/ce02shsm/D00001/superv/dcl12"
for raw in $RAW/ce02shsm/D00001/cg_data/dcl12/superv/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_superv_dcl.py -i $raw -o $OUT/${FILE%.log}.mat
done
OUT="$PARSED/ce02shsm/D00001/superv/dcl26"
for raw in $RAW/ce02shsm/D00001/cg_data/dcl26/superv/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_superv_dcl.py -i $raw -o $OUT/${FILE%.log}.mat
done
OUT="$PARSED/ce02shsm/D00001/superv/dcl27"
for raw in $RAW/ce02shsm/D00001/cg_data/dcl27/superv/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_superv_dcl.py -i $raw -o $OUT/${FILE%.log}.mat
done
