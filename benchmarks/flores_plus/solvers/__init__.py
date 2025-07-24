"""
FLORES+ Translation Solvers

This package contains different translation solvers for the FLORES+ benchmark,
similar to how EXECUTE has different task-specific solvers.
"""

from .direct_translation import direct_translation
from .few_shot_translation import few_shot_translation 
from .zero_shot_translation import zero_shot_translation
from .pivot_translation import pivot_translation

__all__ = [
    "direct_translation",
    "few_shot_translation", 
    "zero_shot_translation",
    "pivot_translation"
] 