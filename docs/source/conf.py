# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'ATLAS VRAs'
copyright = '2024, Heloise Stevance'
author = 'Heloise Stevance'

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

#import sphinx_rtd_theme

html_theme = 'sphinx_book_theme'

#html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]



# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
from atlasvras import __version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]
# The full version, including alpha/beta/rc tags
release = __version__

#templates_path = ['_templates']
#exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/logo.png'