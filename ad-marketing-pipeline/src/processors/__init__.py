# src/processors/__init__.py
"""Data processors for different pipeline layers."""

from .silver_processor import SilverProcessor
from .gold_processor import GoldProcessor

__all__ = ["SilverProcessor", "GoldProcessor"]