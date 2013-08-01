# Autozygosity Standalone Script

## Installation

* You will need to download the analysis tools into `./bin`
* Place the human reference genome in `./ref`  
  It must be called "`hg19.fa`"
* Modify the `BINARY_DIR` variable to the full path to this script
* Then modify paths to the analysis tools and reference genome

### Analysis Tools

* Genome Analysis Toolkit  
http://www.broadinstitute.org/gatk/
   
* VCFTools  
http://vcftools.sourceforge.net/

* PLINK  
http://pngu.mgh.harvard.edu/~purcell/plink/

* SAMtools  
http://samtools.sourceforge.net/

* BEDtools  
http://bedtools.readthedocs.org/en/latest/

### Reference Genome

	http://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/

You'll need the `twoBitToFa` utility to extract the file.

	http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/twoBitToFa

## Using the script 

### Basic usage

	run.sh -i /path/to/input.vcf

This will run with the following default parameters:

* Minimum Variant Quality: 30
* Minimum Quality by Depth: 10
* Homozygosity Window Size: 1000
* Heterozygous Calls Allowed in Window: 10

### Customization

You can modify analysis parameters using the following switches:

	-v   Minimum variant quality
	-d   Minimum quality depth
	-w   Homozygosity window size
	-c   Heterozygous Calls Allowed in Window

For instance:

	run.sh -i input.vcf -w 3000 -v 55

### Output

At the end of a successful analysis, you'll find output BED and VCF files called `output.bed` and `output.ROH.vcf` respectively.
