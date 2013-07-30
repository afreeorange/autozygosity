#!/bin/bash
# Attempt to download specified VCF input. If problems, clean up.

while getopts ":u:e:f:" opt; do
	case $opt in
		u)
			URI=$OPTARG
			;;
		e)
			EXTENSION=$OPTARG
			;;
		f)
			FOLDER=$OPTARG
			;;
	esac
done

echo -e "Attempting to download $URI (a $EXTENSION file) to $FOLDER"

mkdir -p $FOLDER
wget -O $FOLDER/input.$EXTENSION $URI

if [[ $? -ne 0 ]]; then
	rm -rf $FOLDER
	exit 100
fi
