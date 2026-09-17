
from pathlib import Path
from sys import path as sysPath

from typing import Dict
from typing import List
from typing import Tuple

# Configuration file for the Sphinx documentation builder.
# Matches pyumldiagrams documentation configuration.

project:   str = 'codeallyadvanced'
# noinspection PyShadowingBuiltins
copyright: str = '2026, Humberto A. Sanchez II'
author:    str = 'Humberto A. Sanchez II'

projectRoot: Path = Path(__file__).resolve().parent.parent
sysPath.insert(0, str(projectRoot))

# noinspection SpellCheckingInspection
intersphinx_mapping: Dict[str, Tuple[str, None]] = {
    'python': ('https://docs.python.org/3/', None),
}

extensions: List[str] = [
    'sphinx.ext.duration',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'autoapi.extension',
]

autoapi_dirs:                 List[str] = ['../src/codeallyadvanced']
autoapi_ignore:               List[str] = ['*resources*']
autoapi_options:              List[str] = ['members', 'undoc-members', 'show-inheritance', 'show-module-summary', 'imported-members']
autoapi_python_class_content: str       = 'both'
autoapi_member_order:         str       = 'bysource'

templates_path:     List[str] = ['_templates']
exclude_patterns:   List[str] = ['**/resources/**', '*resources*']
todo_include_todos: bool      = True

html_theme:       str       = 'sphinx_rtd_theme'
html_static_path: List[str] = ['_static']
