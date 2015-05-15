#!/bin/bash
#
# Very simple little filter to use with incrontab to make sure we only respond
# to events on specific file types (e.g. ignore the temporary files created by
# rsync, responding only to the final updated file). For our purposes, we are
# looking for files that end with a .log extension.
#
# All credit to the wonderful folks at stackoverflow:
#
#       http://stackoverflow.com/questions/6383021
#
# C. Wingard 2015-05-15

# set the name of the file that triggered the incron event.
file=$1
shift 1

# test if the file ends with a .log file extension, note this is kinda reverse
# logic. The file patterns will NOT match if the file ends with the .log
# extension. Otherwise, they match. We want to process the file only if we
# don't get a match.
[ "$file" == "${file%$ext}" ] || $*