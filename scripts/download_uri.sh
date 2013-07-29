#!/bin/bash

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

echo -e $URI
echo -e $EXTENSION
echo -e $FOLDER

mkdir -p $FOLDER
wget -O $FOLDER/input.$EXTENSION $URI

if [[ $? -ne 0 ]]; then
	exit 100
fi
