from setuptools import setup
from setuptools import find_packages


install_requires = [
    'setuptools',
    'numpy',
    'lxml',
    'sphinxcontrib-bibtex',
    'sphinxcontrib-programoutput',
    # -*- Extra requirements: -*-
]

entry_points = {
    'console_scripts': [
        'eelap_generator = eelap.generator:main'
    ]
}


classifiers = [
    'Programming Language :: Python',
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
]

with open("README.md") as f:
    README = f.read()

with open("CHANGES.txt") as f:
    CHANGES = f.read()

setup(name='eelap',
      version='0.3.1',
      packages=find_packages(),
      description=("End-to-End Latency Analysis for ProCom"),
      long_description=README + '\n' + CHANGES,
      author='Jiri Kuncar',
      author_email='jiri.kuncar@gmail.com',
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      keywords='latency analysis ProCom',
      url='https://github.com/jirikuncar/eelap/',
      license='gpl',
      entry_points=entry_points,
      )
