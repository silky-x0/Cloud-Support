import uuid
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Optional, Generator

# Context variable to store the trace_id for the current execution context (e.g., a single request)
_trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def get_trace_id() -> Optional[str]:

    return _trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
 
    _trace_id_var.set(trace_id)


@contextmanager
def trace_context(trace_id: Optional[str] = None) -> Generator[str, None, None]:

    if trace_id is None:
        trace_id = str(uuid.uuid4())

    token = _trace_id_var.set(trace_id)
    try:
        yield trace_id
    finally:
        _trace_id_var.reset(token)
