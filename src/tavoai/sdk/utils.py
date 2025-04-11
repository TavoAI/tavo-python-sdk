"""Utility functions for the TavoAI SDK."""

import logging
import sys
from typing import Optional

# Optional colorlog import - will use it if available, otherwise falls back to standard logging
try:
    import colorlog
    HAS_COLORLOG = True
except ImportError:
    HAS_COLORLOG = False


def configure_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure a logger with the given name and level.
    
    Args:
        name: Name of the logger.
        level: Logging level.
        
    Returns:
        Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create a handler if there are none
    if not logger.handlers:
        handler = logging.StreamHandler(stream=sys.stdout)
        
        if HAS_COLORLOG:
            # Color configuration
            colors = {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
            
            formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                log_colors=colors
            )
        else:
            # Standard formatter without colors
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Prevent propagation to avoid duplicate logs
        logger.propagate = False
    
    return logger 