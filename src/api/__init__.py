"""
API layer for Zero Vector 4
"""

from .agents import router as agents_router
from .consciousness import router as consciousness_router
from .memory import router as memory_router
from .orchestration import router as orchestration_router

__all__ = [
    'agents_router',
    'consciousness_router', 
    'memory_router',
    'orchestration_router'
]
