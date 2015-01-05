from setuptools import setup, find_packages

setup(
    # Application name:
    name="pybraincompare",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Vanessa Sochat",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=["compare"],

    # Data
    package_data = {'compare':['template/*.html']},

    # Details
    url="http://www.vbmis.com/blog",

    license="LICENSE.txt",
    description="Content-aware image comparison",

    install_requires = ['scikit-learn','nibabel','nilearn','pandas','matplotlib','scikit-image']
)
