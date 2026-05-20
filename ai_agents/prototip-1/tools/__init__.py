"""Tool registry: ad → (callable, JSON schema)."""
from __future__ import annotations

from .calculator import calculator, SCHEMA as CALC_SCHEMA
from .web_search import web_search, SCHEMA as SEARCH_SCHEMA
from .fs import read_file, write_file, READ_SCHEMA, WRITE_SCHEMA
from .http_fetch import http_get, SCHEMA as HTTP_SCHEMA

TOOL_REGISTRY = {
    "calculator": calculator,
    "web_search": web_search,
    "read_file": read_file,
    "write_file": write_file,
    "http_get": http_get,
}

TOOL_SCHEMAS = [
    CALC_SCHEMA,
    SEARCH_SCHEMA,
    READ_SCHEMA,
    WRITE_SCHEMA,
    HTTP_SCHEMA,
]
