# CGSN Parsers

Simple python modules and shell script utilities used to parse the raw data 
files logged by the custom built CGSN data logger systems. Resulting parsed 
data is saved in .MAT files for further analysis and plotting by using either
[matlab](http://www.mathworks.com) or the [matplotlib](http://matplotlib.org)
python library.

These parsers do not convert the data values (for the most part) within the
raw data files. In other words, if a particular measurement contained in the
raw data file is reported in counts, the parser does not convert that value to
scientific units. These parsers simply convert the data from the different formats
found in the raw log files (binary, ASCII, ASCIIHEX, mixed ASCII/binary, etc) into
a common format that can be used for further processing. 

An exception to the above applies to calculating an Epoch time stamp (seconds 
since 1970-01-01) from the date and time string information contained in the files.
The prefered source of time is the DCL timestamp as those systems are synced to GPS
via a LAN NTP server.

# Usage

Current usage is for monitoring the system health of the moorings (hydrogen
concentration levels, battery voltages, leak detect currents, etc) and a select
set of instruments providing an assessment of current environmental conditions
(e.g. surface meteorological conditions, wave field and subsurface currents)
for mission planning and troubleshooting (low salinity surface water from the
Columbia River Plume may impact the ability of gliders to surface).

Additionally, parsed data will be compared to the output from other systems for
integration testing and verification. The code is provided as-is for other
users who may wish to interact directly with the [raw data](https://rawdata.oceanobservatories.org/files/).

# Directory Organization

Shell scripts in the utilities/harvesters directory are presented as an example 
of how to collect data from the different instrument systems installed on a 
mooring, either individually or via a `master_harvester.sh` shell script. These
scripts set the input and output directories for the data and call the
appropriate python parser (located in the cgsn_parsers directory) to use with
that instrument. It should be noted that these scripts were created with a
specific user and system in mind. Users will need to adapt these scripts to
fit their own needs.

Some sample plots, with the Matlab code for creating them, are available in the
utilities/plotting directory as an example for how to work with the resulting
data files.

# Requirements

This code was written and tested against Python 2.7.12 using Anaconda from
[Continuum Analytics](https://www.continuum.io/).

The following additional python packages are used by this code:

   * numpy >= 1.9.2
   * scipy >= 0.15.1
   * matplotlib >= 1.4.3
   * munch >= 2.0.4 
   * argparse >= 1.3.0

# Contributing

Users are encouraged to contribute to this code. The hope is this repository can
provide the science community with a means of accessing the raw mooring data. To
contribute, please fork the main
[repo](https://github.com/ooi-integration/cgsn-parsers) to your github account,
create a branch, do your work, and then (when satisfied) submit a pull request to
have your work integrated into the main project repo.
