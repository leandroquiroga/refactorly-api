from __future__ import annotations

import logging
import structlog

def configure_logging(log_level: str = "INFO") -> None:
    """Set up structlog with console output in dev-friendly format"""
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(colors=True)
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict
    )
    
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper())
    )
    