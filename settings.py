PROJECT_NAME = "Test Project"
PROJECT_PATH = "/Users/nikhil/Dropbox/autozygosity/" # Trailing slash required!
HOST="0.0.0.0"
PORT=5000
DEBUG = True
SECRET_KEY = "8MfeRORkN74/dsXMW/78BeLOu1yquSw7"
MONGODB_SETTINGS = {'DB': "autozygosity", 'PORT': 27017}
COPYRIGHT_MESSAGE = """
<a href="http://genome.uiowa.edu">The Center for Bioinformatics &amp; Computational Biology</a> at <a href="http://www.uiowa.edu">The University of Iowa</a>
<br />
Email <a href="mailto:nikhil-anand@uiowa.edu">Nikhil Anand</a> with any questions or issues.
<br />
Built with Flask, Bootstrap, and MongoDB. Source code <a href="#">at GitHub</a>. 
"""
CSRF_ENABLED = True

# Upload settings
UPLOADED_VCF_DEST  = PROJECT_PATH + "uploads"
UPLOADED_VCF_ALLOW = "vcf"
UPLOADED_VCF_MAX_SIZE = 108 * 1024 * 1024

# Job status definitions (and associated CSS classes)
JOB_STATUSES = ('submitted', 'running', 'completed', 'failed')
STATUS_CLASSES = ('', 'label-info', 'label-success', 'label-important')
STATUS_MAP = dict(zip(JOB_STATUSES, STATUS_CLASSES))
