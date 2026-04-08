# Configuration file for the Sphinx documentation builder.

import os
import sys
import django

sys.path.insert(0, os.path.abspath("../.."))
os.environ["DJANGO_SETTINGS_MODULE"] = "news_project.settings"
django.setup()

# -- Project information -----------------------------------------------------

project = "news_project"
copyright = "2026, Rodrigo Machado"
author = "Rodrigo Machado"
release = "4/08/26"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_theme = "alabaster"
html_static_path = ["_static"]