# Homozygosity Mapping

Homozygosity Mapping is a powerful technique used to narrow the search space for disease-causing variants in exome sequencing data. This has traditionally been performed using a separate micro-array based experiment, but with costs of exomes continuing to fall, homozygosity mapping can be performed using only exome sequence.

This project is the public, anonymous, token-based front end to the analysis tool, which can retain the region containing the disease-causing variant in a consanguineous pedigree, while eliminating XXX% of identified variants from consideration.

## Requirements

### Web Server

* A *NIX server with the `bash` interpreter
* `unzip`, `tar`, `unrar`, `unrar`, `bunzip2`
* Python 2.7
* Java 1.7
* Perl
* A running MongoDB server
* A running Nginx server

### Analysis Tools

* The [Genome Analysis Toolkit](http://www.broadinstitute.org/gatk/)
* [VCFTools](http://vcftools.sourceforge.net/)
* [PLINK](http://pngu.mgh.harvard.edu/~purcell/plink/)
* [SAMtools](http://samtools.sourceforge.net/)
* [BEDtools](http://bedtools.readthedocs.org/en/latest/)

## Installation & Configuration

* Run `install` first. It should take care of most requirements for you. 

	* If you're using an RHEL-based system, edit [line 17 of `install`](https://github.com/afreeorange/autozygosity/blob/master/install#L17)and modify the `virtualenv` command to point at a compiled version of Python 2.7

			virtualenv -p /path/to/python2.7 .

* Modify `settings.py` to suit your environment.
* Look at `scripts/run.sh` to configure paths to the genomic analysis tools required.
* Make sure that `client_max_body_size` is set to whatever you limit your upload sizes to in Nginx's `http {…}` section. 
* Place a sample VCF file called "`sample.vcf`" in `autozygosity/static/`
* Go through the `configs/` folder to install cron and logrotate entries.

Once you've taken care of these, you can start the server:

	source ./bin/activate	
	./start

Unless you've changed some parameters, this will start ten Gunicorn workers, with the parent listening at `127.0.0.1:5000`. Stop the server with:

	./stop

If you want a Flask server for testing,

	./start flask

It's highly recommended that you set `DEBUG = False` in `settings.py` and use Nginx as a reverse proxy to Gunicorn. See the `configs/` folder for a sample configuration.

## License

See `LICENSE`
