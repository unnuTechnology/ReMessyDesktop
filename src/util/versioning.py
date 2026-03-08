import sys
from os import path
import datetime
import tomllib


with open('pyproject.toml', 'rb') as f:
    project = tomllib.load(f)['project']

VERSION_CODE = project['version']
VERSION_FULL = f"v{VERSION_CODE} Codename {project['version-codename']}"
BUILD_CODE = (
    f"remessydesktop-build-v{VERSION_CODE}-{project['version-codename'].replace(' ', '')}-"
    f"{datetime.datetime.fromtimestamp(path.getmtime('.')).strftime('%Y%m%d-%H%M%S.%f')}-{sys.platform}"
)
