
import pathlib

from setuptools import setup

from codeallyadvanced import __version__ as version


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
LICENSE = (HERE / 'LICENSE').read_text()

setup(
    name="codeallyadvanced",
    version=version,
    author='Humberto A. Sanchez II',
    author_email='Humberto.A.Sanchez.II@gmail.com',
    maintainer='Humberto A. Sanchez II',
    maintainer_email='humberto.a.sanchez.ii@gmail.com',
    description='Humberto`s Common UI Stuff',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hasii2011/code-ally-advanced",
    package_data={
        'codeallyadvanced':                        ['py.typed'],
        'codeallyadvanced.resources':              ['py.typed'],
        'codeallyadvanced.resources.images':       ['py.typed'],
        'codeallyadvanced.resources.images.icons': ['py.typed'],
        'codeallyadvanced.resources.images.icons.embedded16': ['py.typed'],
        'codeallyadvanced.resources.images.icons.embedded32': ['py.typed'],

        'codeallyadvanced.ui':         ['py.typed'],
        'codeallyadvanced.ui.widgets': ['py.typed'],
    },

    packages=[
        'codeallyadvanced',
        'codeallyadvanced.resources',
        'codeallyadvanced.resources.images',
        'codeallyadvanced.resources.images.icons',
        'codeallyadvanced.resources.images.icons.embedded16',
        'codeallyadvanced.resources.images.icons.embedded32',
        'codeallyadvanced.ui', 'codeallyadvanced.ui.widgets'
    ],
    install_requires=['codeallybasic~=1.0.0', 'wxPython~=4.2.1'],
)
