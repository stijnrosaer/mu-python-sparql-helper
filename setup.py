import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mu-SPARQL-helpers",
    version="0.0.1",
    author="Stijn Rosaer",
    author_email="stijn.rosaer@telenet.be",
    description="Python helper for SPARQL for a mu.semte.ch stack",
    long_description=long_description,
    python_requires=">=3.6",
    install_requires=[
        "flask",
        "requests",
        "SPARQLWrapper",
        "rdflib"
    ],
    url="https://github.com/stijnrosaer/mu-python-sparql-helper",
    packages=setuptools.find_packages(),
    keywords = ["mu", "sparql"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)