# CGSN Parsers

Simple python modules and shell script utilities used to parse the raw data 
files logged by the custom built CGSN data logger systems. Resulting parsed 
data is saved in .MAT files for further analysis and plotting by using either
[matlab](http://www.mathworks.com) or the [matplotlib](http://matplotlib.org)
python library.

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

Shell scripts in the utilities/harvester directory are presented as an example 
of how to collect data from the different instrument systems installed on a 
mooring, either individually or via a `master_harvester.sh` shell script. These
scripts set the input and output directories for the data and call the
appropriate python parser (located in the cgsn_parsers directory) to use with
that instrument.

Some sample plots, with the Matlab code for creating them, are available in the
utilities/plotting directory as an example for how to work with the resulting
data files.

# Requirements

This code was written and tested against Python 2.7.9

The following additional python packages are used by this code:

   * numpy >= 1.9.2
   * scipy >= 0.15.1
   * matplotlib >= 1.4.3
   * bunch >= 1.0.1
   * argparse >= 1.3.0
