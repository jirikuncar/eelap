from setuptools import setup
from setuptools import find_packages


install_requires = [
    'setuptools',
    'numpy',
    'lxml',
    # -*- Extra requirements: -*-
]

entry_points = """
    # -*- Entry points: -*-
    """

classifiers = [
    'Programming Language :: Python',
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
]

with open("README.md") as f:
    README = f.read()

with open("CHANGES.txt") as f:
    CHANGES = f.read()

setup(name='eelaf',
      version='0.1',
      packages=find_packages(),
      description=("End-to-End Latency Analysis Framework"),
      long_description=README + '\n' + CHANGES,
      author='Jiri Kuncar',
      author_email='jiri.kuncar@gmail.com',
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      keywords='latency analysis framework',
      url='https://github.com/jirikuncar/eelaf/',
      license='gpl',
      entry_points=entry_points,
      )
