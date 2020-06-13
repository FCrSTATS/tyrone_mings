from distutils.core import setup

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name="tyrone_mings", # Replace with your own username
    version="1.0",
    author="FC rSTATS",
    author_email="me@fcrstats.com",
    description="A package to help pull information from the transfermarkt website",
    long_description="A package to help pull information from the transfermarkt website",
    long_description_content_type="text/markdown",
    url="https://github.com/FCrSTATS/tyrone_mings",
    package_dir={'tyrone_mings': 'src'},
    packages=['tyrone_mings'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
