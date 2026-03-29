"""Custom exceptions for mono-pixel."""


class MonoPixelError(Exception):
    """Base exception class for all mono-pixel errors."""

    pass


class FontError(MonoPixelError):
    """Base class for font-related errors."""

    pass


class FontNotFoundError(FontError):
    """Raised when a font file cannot be found."""

    pass


class InvalidFontError(FontError):
    """Raised when a font file is invalid or unreadable."""

    pass


class ResourceError(MonoPixelError):
    """Base class for resource-related errors."""

    pass


class ResourceNotFoundError(ResourceError):
    """Raised when a bundled resource cannot be found."""

    pass


class ResourceAccessError(ResourceError):
    """Raised when a bundled resource cannot be accessed."""

    pass
