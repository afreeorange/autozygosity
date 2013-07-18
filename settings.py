from datetime import datetime

PROJECT_NAME = "Test Project"
PROJECT_PATH = "/Users/nikhil/Dropbox/autozygosity/" # Trailing slash required!
HOST="0.0.0.0"
PORT=5000
DEBUG = True
MONGODB_SETTINGS = {'DB': "autozygosity", 'PORT': 27017}
COPYRIGHT_MESSAGE = """
&copy """ + datetime.now().strftime("%Y") + """ <a href="http://genome.uiowa.edu">The Center for Bioinformatics &amp; Computational Biology</a> at <a href="http://www.uiowa.edu">The University of Iowa</a>
<br />
Email <a href="mailto:nikhil-anand@uiowa.edu">Nikhil Anand</a> with any questions or issues.
<br />
Built with Flask, Bootstrap, &amp; MongoDB. Source code <a href="https://github.com/afreeorange/autozygosity" title="Project source code at Github">at GitHub</a>. 
"""
SUBMISSION_RETENTION_DAYS=10

# Upload settings
UPLOADED_VCF_DEST  = PROJECT_PATH + "uploads"
UPLOADED_VCF_ALLOW = "vcf"
UPLOADED_VCF_MAX_SIZE = 108 * 1024 * 1024

# Job status definitions (and associated CSS classes)
JOB_STATUSES = ('submitted', 'running', 'completed', 'failed')
STATUS_CLASSES = ('label-inverse', 'label-info', 'label-success', 'label-important')
STATUS_MAP = dict(zip(JOB_STATUSES, STATUS_CLASSES))

CSRF_ENABLED = True
SECRET_KEY = "8MfeRORkN74/dsXMW/78BeLOu1yquSw7"
TOKEN_REGEX = r'[a-zA-Z]{5,15}'
