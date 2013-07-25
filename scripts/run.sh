#!/bin/bash

# Calculate the regions of autozygosity in a multi-sample VCF and annotate it with those regions
# Uses plink to define regions of >1MB containing <=2 het snps per 1MB sliding window

# Adam DeLuca  <adam-deluca@uiowa.edu>
# Nikhil Anand <nikhil-anand@uiowa.edu>


### Edit these!

BINARY_DIR="/home/adeluca"
REFERENCE=$BINARY_DIR/ref/hg19.fa
GATK=$BINARY_DIR/bin/gatk-master/dist/GenomeAnalysisTK.jar
VCFTOOLS=$BINARY_DIR/bin/vcftools/bin/
PLINK=$BINARY_DIR/bin/plink/plink
TABIX=$BINARY_DIR/bin/tabix/
BEDTOOLS=$BINARY_DIR/bin/bedtools/bin/

### Don't touch anything else.

INPUT_VCF=$1
SAMPLE_DIR=$(dirname $INPUT_VCF)

# Run parameters
MIN_VARIANT_QUALITY=30
MIN_QUALITY_DEPTH=10
HOMOZYG_WINDOW_SIZE=1000
HETEROZYG_CALLS=10

JAVA=$(which java)
PERL=$(which perl)

export PATH=$PATH:/usr/java/latest/bin/:$BINARY_DIR/bin/tabix-0.2.6/
export PERL5LIB=$PERL5LIB:$BINARY_DIR/bin/vcftools_0.1.10/perl/

# Tag low-quality SNPs
$JAVA 	-Xmx8G -jar $GATK \
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
$PERL 	-I $TABIX/perl $VCFTOOLS/vcf-annotate $INPUT_VCF \
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

# Change chr23 to chrX (Plink!!)
sed -i 's/chr23/chrX/' $SAMPLE_DIR/output.bed

# Compress output files
cd $SAMPLE_DIR
zip output.zip output.ROH.vcf output.bed

# Clean up
rm $SAMPLE_DIR/plink* $SAMPLE_DIR/QDfilter* $SAMPLE_DIR/temp_sample* $SAMPLE_DIR/input.vcf.idx
