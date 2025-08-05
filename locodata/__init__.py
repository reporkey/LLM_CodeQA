"""Top‑level package for locodata."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("locodata")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

# Expose key helpers at package root
from .cli import app as cli_app  # noqa: E402
