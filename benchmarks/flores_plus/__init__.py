"""
FLORES+ Translation Benchmark

This package contains translation evaluation tasks for the FLORES+ dataset,
including bidirectional translation capabilities and multiple solver types.
"""

from .flores_plus_eng_to_xx import FloresDatasetProcessor
from .flores_eng_to_target import flores_eng_to_target
from .flores_target_to_eng import flores_target_to_eng
from .flores_bidirectional import flores_bidirectional

__all__ = [
    "FloresDatasetProcessor",
    "flores_eng_to_target",
    "flores_target_to_eng", 
    "flores_bidirectional"
] 