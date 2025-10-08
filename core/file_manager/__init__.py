"""
File Manager Module
==================

Handles GDS file loading, SVG conversion, and SVG parsing.
"""

from .gds_loader import GDSLoader
from .svg_converter import SVGConverter
from .svg_parser import SVGParser

__all__ = ['GDSLoader', 'SVGConverter', 'SVGParser']
