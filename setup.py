import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jazzml",
    version="0.1.0",
    author="Jean-Christophe Mincke",
    author_email="jeanchristophe.mincke@gmail.com",
    description="Decoder for json/yaml documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jcmincke/jazzml",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)