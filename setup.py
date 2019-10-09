import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pvoutput",
    version="0.0.1",
    author="James Hodgkinson",
    author_email="yaleman@ricetek.net",
    description="PVOutput.org interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yaleman/pvoutput",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)