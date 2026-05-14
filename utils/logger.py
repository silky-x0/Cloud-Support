import logging
import json
import sys
import os
from datetime import datetime
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """
    Structured logging formatter that outputs logs in JSON format.
    Merges extra fields passed in the 'extra' parameter directly into the top-level JSON object.
    """

    def format(self, record: logging.LogRecord) -> str:
        from utils.trace import get_trace_id

        # Basic log record structure
        log_record: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }

        # Inject trace_id from context if available
        trace_id = get_trace_id()
        if trace_id:
            log_record["trace_id"] = trace_id

        # Add exception info if it exists
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Standard LogRecord attributes to exclude from the JSON output
        standard_attrs = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
            "taskName",
        }

        # Merge extra fields
        if hasattr(record, "__dict__"):
            for key, val in record.__dict__.items():
                if key not in standard_attrs and not key.startswith("_"):
                    log_record[key] = val

        return json.dumps(log_record)


def setup_logging(level: str = None) -> None:
    from config.settings import settings

    if level is None:
        level = settings.LOG_LEVEL.upper()

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

  
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    root_logger.addHandler(console_handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
