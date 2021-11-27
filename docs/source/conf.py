# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Odoo Business Relationship Types'
copyright = '2021, Michael Jurke'
author = 'Michael Jurke'


# -- General configuration ---------------------------------------------------

# let's not use sphinx.ext.githubpages, because we use jekyll plugins
extensions = [
    # 'sphinx.ext.githubpages',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# input files
source_suffix = '.rst'
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_static_path = ['_static']

html_title = 'Odoo Business Relationship Types Documentation'
html_theme = 'haiku'
html_theme_options = {
    "textcolor": "#000",
    "headingcolor": "#000",
    "linkcolor": "#000",
    "visitedlinkcolor": "#000",
    "hoverlinkcolor": "#000",
}

html_css_files = [
    'custom.css',
]

if tags.has('github'):
    html_context = {
        'github': True,
    }
