DIR = None
LOG_FILE = None
NG = 'node_modules/@angular/cli/bin/ng'

GITLAB_URL = 'https://gitlab.com/api/v4/'
GITLAB_TOKEN = None
GITLAB_PROJECT_ID = None


try:
    from local_settings import *
except ImportError:
    pass
