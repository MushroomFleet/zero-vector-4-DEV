"""
Logging configuration for Zero Vector 4
"""

import logging
import logging.handlers
import sys
from typing import Optional
from pathlib import Path

import structlog
from structlog.stdlib import LoggerFactory

from .config import get_config


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Setup structured logging for Zero Vector 4
    
    Args:
        log_level: Optional log level override
    """
    config = get_config()
    level = log_level or config.log_level
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )
    
    # Setup file handler for persistent logging
    file_handler = logging.handlers.RotatingFileHandler(
        filename=logs_dir / "zero_vector_4.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if config.env == "production" 
            else structlog.dev.ConsoleRenderer(colors=True)
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class AgentLogger:
    """Specialized logger for agent activities"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = get_logger(f"agent.{agent_type}.{agent_id}")
    
    def log_task_start(self, task_id: str, task_type: str, description: str):
        """Log the start of a task"""
        self.logger.info(
            "Task started",
            task_id=task_id,
            task_type=task_type,
            description=description,
            agent_id=self.agent_id,
            agent_type=self.agent_type
        )
    
    def log_task_complete(self, task_id: str, duration_ms: float, success: bool):
        """Log task completion"""
        self.logger.info(
            "Task completed",
            task_id=task_id,
            duration_ms=duration_ms,
            success=success,
            agent_id=self.agent_id,
            agent_type=self.agent_type
        )
    
    def log_consciousness_update(self, consciousness_level: float, metrics: dict):
        """Log consciousness development updates (TLP agents only)"""
        self.logger.info(
            "Consciousness updated",
            consciousness_level=consciousness_level,
            metrics=metrics,
            agent_id=self.agent_id,
            agent_type=self.agent_type
        )
    
    def log_memory_operation(self, operation: str, memory_type: str, count: int = 1):
        """Log memory operations"""
        self.logger.debug(
            "Memory operation",
            operation=operation,
            memory_type=memory_type,
            count=count,
            agent_id=self.agent_id,
            agent_type=self.agent_type
        )
    
    def log_agent_interaction(self, target_agent_id: str, interaction_type: str, success: bool):
        """Log agent-to-agent interactions"""
        self.logger.info(
            "Agent interaction",
            target_agent_id=target_agent_id,
            interaction_type=interaction_type,
            success=success,
            agent_id=self.agent_id,
            agent_type=self.agent_type
        )
    
    def log_error(self, error: Exception, context: dict = None):
        """Log errors with context"""
        self.logger.error(
            "Agent error",
            error=str(error),
            error_type=type(error).__name__,
            context=context or {},
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            exc_info=True
        )


class SystemLogger:
    """System-wide logging utilities"""
    
    def __init__(self):
        self.logger = get_logger("system")
    
    def log_system_startup(self, config_summary: dict):
        """Log system startup"""
        self.logger.info(
            "Zero Vector 4 starting up",
            version="4.0.0",
            config=config_summary
        )
    
    def log_system_shutdown(self, graceful: bool = True):
        """Log system shutdown"""
        self.logger.info(
            "Zero Vector 4 shutting down",
            graceful=graceful
        )
    
    def log_performance_metrics(self, metrics: dict):
        """Log performance metrics"""
        self.logger.info(
            "Performance metrics",
            **metrics
        )
    
    def log_security_event(self, event_type: str, details: dict, severity: str = "info"):
        """Log security events"""
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(
            "Security event",
            event_type=event_type,
            details=details,
            severity=severity
        )


# Global loggers
system_logger = SystemLogger()
