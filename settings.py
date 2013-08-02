from datetime import datetime

PROJECT_PATH = "/opt/autozygosity/" # Trailing slash required!
HOST="127.0.0.1"
PORT=5000
DEBUG = False

PROJECT_NAME = "Homozygosity Mapping"
MONGODB_SETTINGS = {'DB': "autozygosity", 'PORT': 27017}
COPYRIGHT_MESSAGE = """
&copy """ + datetime.now().strftime("%Y") + """ <a href="http://genome.uiowa.edu">The Center for Bioinformatics &amp; Computational Biology</a> at <a href="http://www.uiowa.edu">The University of Iowa</a>
<br />
Email <a href="mailto:nikhil-anand@uiowa.edu">Nikhil Anand</a> with any questions or issues related to this site. 
<br />
Source <a href="https://github.com/afreeorange/autozygosity" title="Project source code at Github">at GitHub</a>
"""
SUBMISSION_RETENTION_DAYS=10

# Form upload settings
UPLOADED_VCF_DEST  = PROJECT_PATH + "uploads/" # Trailing slash required again, Suzy!
UPLOADED_VCF_ALLOW = "vcf"
UPLOADED_VCF_MAX_SIZE = 128 * 1024 * 1024

# URI upload setting
DOWNLOAD_VCF_MAX_SIZE = 512 * 1024 * 24

# Job status definitions (and associated CSS classes)
JOB_STATUSES = ('submitted', 'running', 'completed', 'failed')
STATUS_CLASSES = ('label-inverse', 'label-info', 'label-success', 'label-important')
STATUS_MAP = dict(zip(JOB_STATUSES, STATUS_CLASSES))

CSRF_ENABLED = True
TOKEN_REGEX = r'[a-zA-Z]{5,15}'
UPLOAD_FORMAT_EXTENSIONS = ['vcf', 'rar', 'zip', 'tar', 'tar.gz', 'tgz', 'gz', 'tar.bz', 'tbz', 'bz']
SECRET_KEY="asdklajskldsajkldjaskd"