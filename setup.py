from distutils.core import setup

setup(
    # Application name:
    name="pybraincompare",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Vanessa Sochat",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=["brain"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://www.vbmis.com/blog",

    license="LICENSE.txt",
    description="Content-aware image comparison",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "nibabel",
        "numpy",
        "pandas",
        "nilearn",
    ],
)
