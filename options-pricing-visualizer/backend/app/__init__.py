"""Backend package for the Options Pricing Visualizer.

This module intentionally exposes the Black-Scholes engine and provides
package metadata. Keeping a small `__init__` helps imports read nicely
and documents the package intent.
"""

__all__ = ["price_and_greeks", "SUPPORTED_GREEKS"]

from .bs import price_and_greeks, SUPPORTED_GREEKS
