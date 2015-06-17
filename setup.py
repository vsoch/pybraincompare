from setuptools import setup, find_packages

setup(
    # Application name:
    name="pybraincompare",

    # Version number (initial):
    version="0.1.10",

    # Application author details:
    author="Vanessa Sochat",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data
    package_data = {'pybraincompare.template':['html/*.html','static/*.zip','js/*.js','css/*.css','img/*'],
                    'pybraincompare.testing':['data/*.tsv','data/*.csv'],
                    'pybraincompare.mr':['*.nii','*.nii.gz','*.xml']},

    # Details
    url="http://www.github.com/vsoch/pybraincompare",

    license="LICENSE.txt",
    description="image-based meta analysis and comparison for neuroimaging in python",

    install_requires = ['six','pydicom','Cython','networkx','numpy','scipy','scikit-learn','nibabel','nilearn','pandas','matplotlib','scikit-image','cairocffi']
)
