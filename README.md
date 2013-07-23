# Homozygosity Mapping

---

Homozygosity Mapping is a powerful technique used to narrow the search space for disease-causing variants in exome sequencing data. This has traditionally been performed using a separate micro-array based experiment, but with costs of exomes continuing to fall, homozygosity mapping can be performed using only exome sequence.

This project is the public, anonymous, token-based front end to the analysis tool, which can retain the region containing the disease-causing variant in a consanguineous pedigree, while eliminating XXX% of identified variants from consideration.

## Requirements

### Web Server

* A *NIX server with the `bash` interpreter
* Python 2.7
* A running MongoDB server
* Java

### Analysis Tools

* The [Genome Analysis Toolkit](http://www.broadinstitute.org/gatk/)
* [VCFTools](http://vcftools.sourceforge.net/)
* [PLINK](http://pngu.mgh.harvard.edu/~purcell/plink/)
* [SAMtools](http://samtools.sourceforge.net/)
* [BEDtools](http://bedtools.readthedocs.org/en/latest/)


## Installation & Configuration

* Run `install` first. It should take care of most requirements for you.
* Modify `settings.py` to suit your environment.
* Look at `scripts/run.sh` to figure out where to place the genomic analysis tools in `scripts/bin` and `scripts/ref`

You can now start the server:

	source ./bin/activate	
	./start

This will start ten Gunicorn threads. Stop the server with:

	./stop

If you want a Flask server for testing,

	./start flask

## License

See `LICENSE`