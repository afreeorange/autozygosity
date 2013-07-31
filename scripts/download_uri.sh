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

echo -n "Attempting to download $URI to $FOLDER... "

mkdir -p $FOLDER
wget -O $FOLDER/input.$EXTENSION $URI --quiet

if [[ $? -ne 0 ]]; then
	rm -rf $FOLDER
	echo -e "failed."
	exit 100
else
	echo -e "done."
fi
