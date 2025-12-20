import tomllib


with open("pyproject.toml", "rb") as f:
    project = tomllib.load(f)["project"]


VERSION_CODE = project["version"]
VERSION_FULL = f"v{VERSION_CODE} Codename {project['version-codename']}"
