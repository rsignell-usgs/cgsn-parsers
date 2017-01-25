# CGSN Parsers

Simple python modules and shell script utilities used to parse and process the
raw data files logged by the custom built CGSN data logger systems. Resulting
parsed and/or processed data is saved in .JSON files for further analysis and
plotting.

There are separate sets of modules contained herein: parsers and processors.

The parsers simply convert the data from the different formats found in the raw
log files (binary, ASCII, ASCIIHEX, mixed ASCII/binary, etc) into a common
format (JSON) that can be used for further processing. They do not convert the
data values (for the most part) found within the raw data. In other words, if a
particular measurement contained in the raw data file is reported in counts, the
parser does not convert that value to scientific units.

An exception to the above applies to calculating an Epoch time stamp (seconds 
since 1970-01-01) from the date and time string information contained in the files.
The prefered source of time is the DCL timestamp as those systems are synced to GPS
via a LAN NTP server.

The processors take the parsed data through the next step of converting values
from engineering units (e.g. counts or volts) to scientific units, applying
factory calibrations, or calculating new values (e.g. salinity and density for
the CTD data). The processors take advantage of the body of code found in
[ion-functions](https://github.com/ooici/ion-functions). That imposes some
constraints on working with this code, but a knowledgeable user should be able
to work through and around them.

# Usage

Current usage is for monitoring the system health of the moorings (hydrogen
concentration levels, battery voltages, leak detect currents, etc) and a select
set of instruments providing an assessment of current environmental conditions
(e.g. surface meteorological conditions, wave field and subsurface currents)
for mission planning and troubleshooting (low salinity surface water from the
Columbia River Plume may impact the ability of gliders to surface).

Additionally, parsed and processed data will be compared to the output from
other systems for integration testing and verification. The code is provided
as-is for other users who may wish to interact directly with the [raw
data](https://rawdata.oceanobservatories.org/files/).

# Directory Organization

The python code for this project is available in the cgsn_parsers direcory.

Examples for how to work with some of the parsers and processors are presented
in the notebooks directory using [Jupyter](http://jupyter.org/) Notebooks.

Shell scripts in the utilities/harvesters directory are presented as an example
of how to collect data from the different instrument systems installed on a
mooring, either individually or via a `master_harvester.sh` shell script. These
scripts set the input and output directories for the data and call the
appropriate python parser (located in the cgsn_parsers directory) to use with
that instrument. It should be noted that these scripts were created with a
specific user and system in mind. Users will need to adapt these scripts to fit
their own needs.

Additional shell scripts in the utilities/processors directory are provided as
examples of how to process the parsed data (e.g. converting values to scientific
units, deriving new values, applying factory calibrations, etc). 

Some sample plots, with the Matlab code for creating them, are available in the
utilities/plotting directory as an example for how to work with the resulting
data files.

# Requirements

This code was written and tested against Python 2.7.12 using Anaconda from
[Continuum Analytics](https://www.continuum.io/).

The following additional python packages are used by this code:

   * gsw >= 3.0.3 (if planning on supplementing ion-functions)
   * numpy >= 1.9.2
   * scipy >= 0.15.1
   * matplotlib >= 1.4.3
   * munch >= 2.0.4 
   * argparse >= 1.3.0
   
Additionally, users will need to obtain a copy of
[ion-functions](https://github.com/ooici/ion-functions) if they want to use the
processors (can be ignored if just using the parsers). This part does require
some effort and consideration. Some elements of the ion-functions code requires
compiling C code on a Linux system and installing shared libraries. If those
functions are not used (and they basically are not in this project), then the
user simply needs to clone ion-functions to their local machine (OS
independent), add the ion-functions directory to their PYTHONPATH, and proceed.
If you do want the functions, on a Linux or Mac (example below tested on a
CentOS 6 machine using Anaconda):

First, use of a few functions in ion-functions requires the
[TEOS-10](http://www.teos-10.org/) C code compiled and installed as a shared
library.

**On OSX**  

The libgswteos dependency is brew installable:

    brew tap lukecampbell/homebrew-libgswteos
    brew install libgswteos-10
    brew test -v libgswteos-10

**On Linux**

The dependencies for building/installing the library are: **autoconf**,
**automake**, & **libtool**
    
1. Obtain the tarball from: https://github.com/lukecampbell/gsw-teos/tarball/v3.0r4
    * sha1: 6ae190b7da78d6aff7859e7d1a3bb027ce6cc5f3

1. Build Procedure

        bash ./autogen.sh  
        ./configure --prefix=/usr/local/libgswteos-10  
        make  
        sudo make install  

1. Linking Procedure:

        sudo ln -s /usr/local/libgswteos-10/lib/libgswteos-10.la /usr/local/lib/  
        sudo ln -s /usr/local/libgswteos-10/lib/libgswteos-10.so.3 /usr/local/lib/  
        sudo ln -s /usr/local/libgswteos-10/lib/libgswteos-10.so.3.0.0 /usr/local/lib/  
        sudo ln -s /usr/local/libgswteos-10/lib/libgswteos-10.so /usr/local/lib/  
        sudo ln -s /usr/local/libgswteos-10/include/gswteos-10.h /usr/local/include/  

1. Ensure that the global `C_INCLUDE_PATH` and `LD_LIBRARY_PATH` includes
/usr/local/lib and /usr/local/include in all profiles otherwise python won't
run correctly:

        echo | gcc -v -Wl,--verbose -x c -E -

1. Check the output, /usr/local/include should be one of the defaults in the
search path). If not (it should be), add the following to your
.bash_profile:

        export C_INCLUDE_PATH=$C_INCLUDE_PATH:/usr/local/include     

1. Check that /usr/local/lib is part of the LIBRARY_PATH. If it is:

        ldconfig -v | grep -v ^$'\t'
        
If not (as root), 
        
        echo "/usr/local/lib" > /etc/ld.so.conf.d/usr_local.conf
        ldconfig

Depending on how the user operates python on their system (strongly recommend
creating a virtual python environment via either
[virtualenv](https://virtualenv.readthedocs.org/en/latest/) or [Continum
Analytics Anaconda python](https://www.continuum.io/why-anaconda)), some
alteration of the setup.py file in ion-functions will be required.

The section to edit is the "install_requires" list in the setup section. Simply
delete all entries other than pygsw and geomag (making sure to install those
packages via pip or conda if not already installed). Then, using either Anaconda
or a Virtual Environment:

```
# using Anaconda
cd <ion-functions-dir>
source activate <cgsn-virtualenv>
conda install numpy scipy cython nose readline numexpr
# be sure to edit setup.py to remove above packages from install_requires
pip install -e /<local_path>/ion-funtions
```
```
# using Virtualenv
cd <ion-functions-dir>
activate <cgsn-virtualenv>
pip install numpy scipy cython nose readline numexpr
pip install -e /<local_path>/ion-funtions
```

Alternatively, clone [ion-functions](https://github.com/ooici/ion-functions)
onto your computer, add the root directory (ion-functions) to your PYTHONPATH,
and call the various python modules therein directly. I've worked with it this
way on my PC and on Linux. Instead of using the TEOS-10 code outlined in
[ion-functions](https://github.com/ooici/ion-functions), I use the python
package GSW. The TEOS-10 functions are largely confined to the ctd_functions.

# Contributing

Users are encouraged to contribute to this code. The hope is this repository can
provide the science community with a means of accessing and working with the raw
mooring data. To contribute, please fork the main
[repo](https://github.com/ooi-integration/cgsn-parsers) to your github account,
create a branch, do your work, and then (when satisfied) submit a pull request
to have your work integrated back into the main project repo.
