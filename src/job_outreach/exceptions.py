class OutreachError(Exception):
    """Base class for expected failures. `status_code` maps to the HTTP response."""

    status_code = 500


class ScrapeError(OutreachError):
    status_code = 502


class LLMError(OutreachError):
    status_code = 502


class ExtractionError(OutreachError):
    status_code = 502


class ResumeError(OutreachError):
    status_code = 422


class LLMNotConfiguredError(OutreachError):
    status_code = 503
