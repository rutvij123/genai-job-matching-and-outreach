"""GenAI job matching and cold-email outreach."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("job-outreach")
except PackageNotFoundError:  # running from source without install
    __version__ = "0.0.0"
