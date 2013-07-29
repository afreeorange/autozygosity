#!/bin/bash

# Calculate the regions of autozygosity in a multi-sample VCF and annotate it with those regions
# Uses plink to define regions of >1MB containing <=2 het snps per 1MB sliding window

# Original script by Adam DeLuca  <adam-deluca@uiowa.edu>
# Adapted for web interface by Nikhil Anand <nikhil-anand@uiowa.edu>

### Edit these!

BINARY_DIR="/home/adeluca"
JAVA=$(which java)
PERL=$(which perl)

BEDTOOLS=$BINARY_DIR/bin/bedtools/bin/
GATK=$BINARY_DIR/bin/gatk-master/dist/GenomeAnalysisTK.jar
PLINK=$BINARY_DIR/bin/plink/plink
REFERENCE=$BINARY_DIR/ref/hg19.fa
TABIX=$BINARY_DIR/bin/tabix/
VCFTOOLS=$BINARY_DIR/bin/vcftools/bin/

export PATH=$PATH:$TABIX:/usr/java/latest/bin/
export PERL5LIB=$PERL5LIB:$BINARY_DIR/bin/vcftools/perl/

### Don't touch anything else. You're safe now, Timmy.

IS_ARCHIVE=1
SAMPLE_DIR=""
UPLOADED_VCF=""
INPUT_VCF=""

# Run parameters
MIN_VARIANT_QUALITY=30
MIN_QUALITY_DEPTH=10
HOMOZYG_WINDOW_SIZE=1000
HETEROZYG_CALLS=10

while getopts ":i:v:d:w:c:" opt; do
	case $opt in
		i)
			UPLOADED_VCF=$OPTARG
			;;
		v)
			MIN_VARIANT_QUALITY=$OPTARG
			;;
		d)
			MIN_QUALITY_DEPTH=$OPTARG
			;;
		w)
			HOMOZYG_WINDOW_SIZE=$OPTARG
			;;
		c)
			HETEROZYG_CALLS=$OPTARG
			;;
	esac
done
SAMPLE_DIR=$(dirname $UPLOADED_VCF)

# Now try to extract the file with some filesystem gymnastics

echo -e "Trying to extract $UPLOADED_VCF"
mkdir -p $SAMPLE_DIR/extraction_temp
cp $UPLOADED_VCF $SAMPLE_DIR/extraction_temp/
cd $SAMPLE_DIR/extraction_temp/
EXTRACTABLE=$SAMPLE_DIR/extraction_temp/$(basename $UPLOADED_VCF)
echo -e "Copied to $EXTRACTABLE"

case $EXTRACTABLE in
	*.rar)
		unrar x $EXTRACTABLE 
		;;
	*.zip)
		unzip $EXTRACTABLE 
		;;
	*.tar)
		tar -xvf $EXTRACTABLE
		;;
	*.tar.gz)
		tar -xvzf $EXTRACTABLE
		;;
	*.tgz)
		tar -xvzf $EXTRACTABLE
		;;
	*.gz)
		gunzip $EXTRACTABLE 
		;;
	*.tar.bz)
		tar -xvjf $EXTRACTABLE
		;;
	*.tbz)
		tar -xvjf $EXTRACTABLE
		;;
	*.bz)
		bunzip2 $EXTRACTABLE 
		;;
	*)  
		echo -e "$EXTRACTABLE is probably not an archive." 
		IS_ARCHIVE=0
		;;
esac

# If uploaded VCF is not an archive, get the first extracted file.
# Website provides caveats about compressed uploads, but people can be 'funny'.
if [[ $IS_ARCHIVE -eq 0 ]]; then
	INPUT_VCF=$UPLOADED_VCF
else
	# Two things of concern: dot-files and "__MACOSX" folders
	INPUT_VCF=$(find $SAMPLE_DIR/extraction_temp -type f ! -iname ".*" ! -iname $(basename $UPLOADED_VCF) | head -1)
	if [[ $INPUT_VCF == "" ]]; then
		echo -e "$UPLOADED_VCF is an archive but not in the expected format."
		exit 100
	fi
fi

echo -e "Input VCF is $INPUT_VCF"

echo -e "MIN_VARIANT_QUALITY: $MIN_VARIANT_QUALITY"
echo -e "MIN_QUALITY_DEPTH: $MIN_QUALITY_DEPTH"
echo -e "HOMOZYG_WINDOW_SIZE: $HOMOZYG_WINDOW_SIZE"
echo -e "HETEROZYG_CALLS: $HETEROZYG_CALLS"

# ------- Actual analysis begins here -------

# Tag low-quality SNPs
$JAVA   -Xmx8G -jar $GATK \
		-T VariantFiltration \
		--filterExpression "QUAL < $MIN_VARIANT_QUALITY || QD < $MIN_QUALITY_DEPTH" \
		--filterName "LowQD" \
		--variant $INPUT_VCF \
		-R $REFERENCE \
		-o $SAMPLE_DIR/QDfilter.vcf

if [ $? -ne 0 ]; then
	echo -e "! Tagging failed on $INPUT_VCF";
	exit 200
fi

# Remove low-quality SNPs
grep -v LowQD $SAMPLE_DIR/QDfilter.vcf > $SAMPLE_DIR/QDfilter.filt.vcf

# Make PED/MAP file for plink. Remove any site with a missing genotype.
$VCFTOOLS/vcftools 	--vcf $SAMPLE_DIR/QDfilter.filt.vcf \
					--plink \
					--out $SAMPLE_DIR/temp_sample \
					--max-missing-count 0
mv $SAMPLE_DIR/temp_sample.map $SAMPLE_DIR/temp_sample.map.old
sed "s/chr//" $SAMPLE_DIR/temp_sample.map.old > $SAMPLE_DIR/temp_sample.map

if [ $? -ne 0 ]; then
	echo -e "! VCFtools failed on $INPUT_VCF";
	exit 300
fi

# Plink analysis
$PLINK 	--file $SAMPLE_DIR/temp_sample \
		--noweb --homozyg --homozyg-group \
		--homozyg-window-kb $HOMOZYG_WINDOW_SIZE \
		--homozyg-window-het $HETEROZYG_CALLS \
		--out $SAMPLE_DIR/plink > /dev/null

# # Put the plink log in the SGE job log file
# cat $SAMPLE_DIR/plink.log

if [ $? -ne 0 ]; then
	echo -e "! Plink analysis failed on $INPUT_VCF";
	exit 400
fi

# Format plink output as a BED file
# CHR   START   END KB_HOM  SNPs_HOM
grep CON $SAMPLE_DIR/plink.hom.overlap | awk '{print "chr"$5"\t"$8"\t"$9"\t"$10"\t"$11}' | $BEDTOOLS/sortBed > $SAMPLE_DIR/plink_ROH.bed
$TABIX/bgzip $SAMPLE_DIR/plink_ROH.bed
$TABIX/tabix -p bed $SAMPLE_DIR/plink_ROH.bed.gz

if [ $? -ne 0 ]; then
	echo -e "! Tabix failed on $INPUT_VCF";
	exit 500
fi

# Annotate the original VCF with the identified regions
$PERL -I $TABIX/perl $VCFTOOLS/vcf-annotate $INPUT_VCF \
		-a $SAMPLE_DIR/plink_ROH.bed.gz \
		-c CHROM,FROM,TO,INFO/PLINK_HOM_KB,- \
		-d "key=INFO,ID=PLINK_HOM_KB,Number=A,Type=Float,Description='Length of region of autozygosity in kb'" \
		> $SAMPLE_DIR/output.ROH.vcf

if [ $? -ne 0 ]; then
	echo -e "! Annotation failed on $INPUT_VCF";
	exit 600
fi

gunzip $SAMPLE_DIR/plink_ROH.bed.gz
mv $SAMPLE_DIR/plink_ROH.bed $SAMPLE_DIR/output.bed

# Change chr23 to chrX (Else UCSC won't like file. Plink!!)
sed -i 's/chr23/chrX/' $SAMPLE_DIR/output.bed

# Compress output files
cd $SAMPLE_DIR
zip output.zip output.ROH.vcf output.bed

# Clean up
rm -rf $SAMPLE_DIR/plink* $SAMPLE_DIR/QDfilter* $SAMPLE_DIR/temp_sample* $SAMPLE_DIR/input.vcf.idx $SAMPLE_DIR/extraction_temp/
