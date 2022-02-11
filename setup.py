from setuptools import setup, find_packages
from flask_thiccutils import __version__, __license__

setup(
    name='ThiccFlaskUtils',
    version=__version__,
    license=__license__,
    description="",
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    url='https://isthicc.dev/',
    author='IsThicc Software',
    packages=find_packages(),
    install_requires=["beaker", "flask", "werkzeug"]
)