#!/bin/bash
# Attempt to download specified VCF input. If problems, clean up.

# Define some defaults
FILENAME="input"
EXTENSION="vcf"
FOLDER="."
MAX_SIZE="134217728" # 128 MiB

while getopts ":u:e:d:f:m:" opt; do
	case $opt in
		u)
			URI=$OPTARG
			;;
		e)
			EXTENSION=$OPTARG
			;;
		d)
			FOLDER=$OPTARG
			;;
		f)
			FILENAME=$OPTARG
			;;
		m)
			MAX_SIZE=$OPTARG
			;;
	esac
done

if [[ -z $URI ]]; then
	echo -e "
`basename $0` [OPTIONS]

Options
-u   Remote URI for download (required)
-f   Local filename
	 	Default is 'input'
-e   Extension to save remote file with
	 	Default is 'vcf'
-d   Local directory to save remote file into
	 	Default is '.'
-m   Maximum download size
	 	Default is 128 MiB
"
	exit
fi

curl --output $FOLDER/$FILENAME.$EXTENSION \
	 --max-filesize $MAX_SIZE \
	 --create-dirs \
	 --silent \
	 --fail \
	$URI
EXIT_CODE=$?

# http://curl.haxx.se/libcurl/c/libcurl-errors.html
if [[ $EXIT_CODE -eq 22 ]]; then
	echo -e "Couldn't find anything at that URI. Are you sure it's valid?" 2>&1
elif [[ $EXIT_CODE -eq 63 ]]; then
	echo -e "File is larger than maximum allowed URI upload size ($MAX_SIZE bytes)" 2>&1
fi
exit $EXIT_CODE
