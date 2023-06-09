import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
LICENSE = (HERE / 'LICENSE').read_text()

setup(
    name="hasiicommon",
    version="0.3.0",
    author='Humberto A. Sanchez II',
    author_email='Humberto.A.Sanchez.II@gmail.com',
    maintainer='Humberto A. Sanchez II',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='Humberto`s Common Stuff',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hasii2011/hasiicommon",
    package_data={
        'hasiicommon':           ['py.typed'],
        'hasiicommon.resources':              ['py.typed'],
        'hasiicommon.resources.images':       ['py.typed'],
        'hasiicommon.resources.images.icons': ['py.typed'],
        'hasiicommon.resources.images.icons.embedded16': ['py.typed'],
        'hasiicommon.resources.images.icons.embedded32': ['py.typed'],

        'hasiicommon.ui':         ['py.typed'],
        'hasiicommon.ui.widgets': ['py.typed'],
    },

    packages=[
        'hasiicommon',
        'hasiicommon.resources',
        'hasiicommon.resources.images',
        'hasiicommon.resources.images.icons',
        'hasiicommon.resources.images.icons.embedded16',
        'hasiicommon.resources.images.icons.embedded32',
        'hasiicommon.ui', 'hasiicommon.ui.widgets'
    ],
    install_requires=['hasiihelper==0.2.0', 'Deprecated~=1.2.13', 'wxPython~=4.2.1'],
)
