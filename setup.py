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
    packages=['jazzml'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'PyYAML',
      ],
)