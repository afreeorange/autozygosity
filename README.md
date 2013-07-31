# Homozygosity Mapping Service

Homozygosity Mapping is a powerful technique used to narrow the search space 
for disease-causing variants in exome sequencing data. This has traditionally 
been performed using a separate micro-array based experiment, but with costs 
of exomes continuing to fall, homozygosity mapping can be performed using only 
exome sequence.

This project is the public, anonymous, token-based front end to the analysis 
tool, which can retain the region containing the disease-causing variant in a 
consanguineous pedigree, while eliminating XXX% of identified variants from 
consideration.

## Requirements

### Web Server

* A *NIX server with the `bash` interpreter
* `unzip`, `tar`, `unrar`, `unrar`, `bunzip2`, `openssl`
* Python 2.7
* Java 1.7
* Perl
* A running MongoDB server
* A running Nginx server

### Analysis Tools

* The [Genome Analysis Toolkit][gatk]
* [VCFTools][vcftools]
* [PLINK][plink]
* [SAMtools][samtools]
* [BEDtools][bedtools]

## Installation & Configuration

1. Run `install` first. It should take care of most requirements for you.   
**Important**: If you're using an RHEL-based system, edit 
[line 17 of `install`][github_install] and modify the `virtualenv` command to 
point at a compiled version of Python 2.7

		virtualenv -p /path/to/python2.7 .

2. Modify `settings.py` to suit your environment.
3. Look at `scripts/run.sh` to configure paths to the genomic analysis tools required. 
	* It's recommended that you download the required analysis tools in `scripts/bin/`
	* You'll need to place [the hg19 reference][hg19] 
	in `scripts/ref/`. It should be called `hg19.fa`.
4. Place a sample VCF file called "`sample.vcf`" in `autozygosity/static/`.
6. Go through the `configs/` folder for sample cron, logrotate, and nginx 
   configurations. 

Once you've taken care of these, you can start the server:

	source ./bin/activate	
	./start

Unless you've specified otherwise, this will start ten Gunicorn workers, with 
the parent listening at `127.0.0.1:5000`. Stop the server with:

	./stop

If you want a Flask server for testing,

	./start flask

Finally, it's highly recommended that you set `DEBUG = False` in `settings.py` 
and use Nginx as a reverse proxy to Gunicorn. 

## Screenshots

[Dropbox link][dropbox]

## To do

* Log errors
* Better CSS selector-names
* VCF validator
* Progress indicator for URI download

## License

(c) Copyright 2013 Nikhil Anand <mail@nikhil.io> `http://nikhil.io`

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[gatk]: http://www.broadinstitute.org/gatk/
[vcftools]: http://vcftools.sourceforge.net/
[plink]: http://pngu.mgh.harvard.edu/~purcell/plink/
[samtools]: http://samtools.sourceforge.net/
[bedtools]: http://bedtools.readthedocs.org/en/latest/

[github_install]: https://github.com/afreeorange/autozygosity/blob/master/install#L17
[hg19]: http://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/
[dropbox]: https://www.dropbox.com/sh/xx6xzo1g9j23wrj/7m9s5K3iQP/autozygosity#/