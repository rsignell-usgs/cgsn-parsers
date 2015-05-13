#!/bin/bash
#
# Read the raw METBK data files for the Endurance Coastal Surface Moorings and
# create parsed datasets available in Matlab formatted .MAT files for further
# processing and review.
#
# Wingard, C. 2015-04-17

# TODO: Convert this to accept input arguements for platform and deployment names

RAW="/home/nereus/data/Deployments/2014_October/recovered"
PARSED="/home/nereus/data/Moorings/parsed"

# CE01ISSM
OUT="$PARSED/ce01issm/R00002/ctdbp1"
for raw in $RAW/CE01ISSM/cg_data/dcl16/ctdbp1/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_ctdbp.py -i $raw -o $OUT/${FILE%.log}.mat -s 2
done

OUT="$PARSED/ce01issm/R00002/ctdbp2"
for raw in $RAW/CE01ISSM/cg_data/dcl37/ctdbp2/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_ctdbp.py -i $raw -o $OUT/${FILE%.log}.mat -s 2
done

OUT="$PARSED/ce01issm/R00002/ctdbp3"
for raw in $RAW/CE01ISSM/cg_data/dcl17/ctdbp3/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_ctdbp.py -i $raw -o $OUT/${FILE%.log}.mat -s 3
done

# CE06ISSM
OUT="$PARSED/ce06issm/R00001/ctdbp1"
for raw in $RAW/CE06ISSM/cg_data/dcl16/ctdbp1/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_ctdbp.py -i $raw -o $OUT/${FILE%.log}.mat -s 2
done

OUT="$PARSED/ce06issm/R00001/ctdbp3"
for raw in $RAW/CE06ISSM/cg_data/dcl17/ctdbp3/*.log; do
    FILE=`basename $raw`
    python ../parsers/parse_ctdbp.py -i $raw -o $OUT/${FILE%.log}.mat -s 3
done
