class ETLError(Exception):
    """Base class for errors raised by the ETL framework."""


class ExtractionError(ETLError):
    """Raised when a source cannot be read."""


class ValidationError(ETLError):
    """Raised when a record fails validation, if needed."""


class TransformationError(ETLError):
    """Raised when the transformation process itself fails."""


class LoadingError(ETLError):
    """Raised when transformed data cannot be saved."""