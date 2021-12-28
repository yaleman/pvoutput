import setuptools

from src.pvoutput import __version__ as release_version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pvoutput",
    version=release_version,
    author="James Hodgkinson",
    author_email="yaleman@ricetek.net",
    description="PVOutput.org API interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yaleman/pvoutput",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=["requests", "aiohttp"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
