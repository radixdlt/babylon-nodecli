from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, "r") as f:
        reqs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return reqs

setup(
    name="babylon-nodecli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    entry_points= {
        "console_scripts": ["radixnode=radixnode:main"]
    },
    scripts=["radixnode.py"]
)
