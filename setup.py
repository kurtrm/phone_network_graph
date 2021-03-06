"""Setup for creation of Kurt's phone network graph."""
from setuptools import setup


extra_packages = {
    'testing': ['pytest', 'pytest-cov', 'tox', 'faker']
}


setup(
    name='Phone Network Graph',
    description='Module that parses T-Mobile phone bills, cleans the data, and'
                ' visualizes the network graph using d3.js.',
    version=1.0,
    author='Kurt Maurer',
    author_email='kurtrm@gmail.com',
    license='MIT',
    install_requires=['PyPDF2', 'numpy', 'pandas', 'matplotlib'],
    extras_require=extra_packages
)
