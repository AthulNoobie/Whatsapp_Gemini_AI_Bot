# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'WhatsApp Gemini AI Bot'
author = 'AthulNoobie'
release = '1.0.0'
version = '1.0.0'

# -- General configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output

html_theme = 'alabaster'
html_static_path = ['_static']
