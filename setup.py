from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='cgsn_parsers',
    version = '0.1.0',
    description = 'Collection of parsers for working with most of the raw data from OOI Endurance, Global and Pioneer moorings',
    long_description = readme(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Data Parsing :: Scientific :: OOI',
    ],
    keywords = 'OOI Endurance Global Pioneer raw data parsing',
    url = 'http://github.com/ooi-integration/cgsn-parsers',
    author = 'Christopher Wingard',
    author_email = 'cwingard@coas.oregonstate.edu',
    license = 'MIT',
    packages = ['cgsn_parsers'],
    install_requires = [
        'numpy >= 1.9.2',
        'scipy >= 0.15.1',
        'matplotlib >= 1.4.3',
        'bunch >= 1.0.1',
        'argparse >= 1.3.0',
    ],
    include_package_data = True,
    zip_safe = False)
