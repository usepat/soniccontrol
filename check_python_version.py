# utility program for displaying the max and min supported python version of the packages

import requests


def get_max_supported_python_version(package):
    name = package.split('==')[0]
    url = f"https://pypi.org/pypi/{name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        versions = data['releases'].keys()
        max_python_version = None
        for version in versions:
            if len(data["releases"][version]) == 0:
                continue
            requires_python = data['releases'][version][0].get('requires_python', None)
            if requires_python:
                if max_python_version is None or requires_python > max_python_version:
                    max_python_version = requires_python
        return max_python_version
    else:
        return None

# List of packages and their versions
with open("requirements.txt", "r") as f:
    packages = list(map(lambda line: line.strip(), f.readlines()))

for package in packages:
    if package.startswith('-e'):
        continue  # Skip editable packages
    max_version = get_max_supported_python_version(package)
    print(f"{package}: {max_version}")
