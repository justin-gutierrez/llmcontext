"""
Core functionality for LLMContext.
"""

from .detector import FrameworkDetector
from .processor import DocumentationProcessor
from .context import ContextManager

__all__ = ["FrameworkDetector", "DocumentationProcessor", "ContextManager"] 