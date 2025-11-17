from __future__ import annotations

import importlib
import os
import runpy
import sys
from typing import Optional


def load_env_file(env_file: Optional[str]) -> None:
    """Load simple KEY=VALUE pairs from a .env-style file."""
    if not env_file:
        return
    if not os.path.exists(env_file):
        raise FileNotFoundError(env_file)
    with open(env_file, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            if key:
                os.environ.setdefault(key.strip(), value.strip())


def import_app(target: Optional[str]) -> None:
    """Import an application module or execute a Python file to register tools."""
    if not target:
        return
    try:
        importlib.import_module(target)
        return
    except ModuleNotFoundError:
        pass

    if os.path.exists(target):
        path = target
        if os.path.isdir(path):
            sys.path.insert(0, path)
            try:
                importlib.import_module("__init__")
            finally:
                sys.path.remove(path)
            return
        script = path if path.endswith(".py") else f"{path}.py"
        if os.path.exists(script):
            runpy.run_path(script, run_name="__mcp_app__")
            return
    raise ModuleNotFoundError(target)
