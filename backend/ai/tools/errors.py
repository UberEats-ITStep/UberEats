"""
Error types for the MCP/AI tool layer.

Every tool-layer failure is expressed as one of these so callers (the
orchestrator, views, tests) can handle them uniformly without needing
to know which specific tool raised them.
"""


class ToolError(Exception):
    """Base class for all tool-layer errors."""

    code = "tool_error"

    def __init__(self, message=None):
        message = message or self.code
        super().__init__(message)
        self.message = message


class ToolNotFoundError(ToolError):
    """Raised when a tool name isn't registered."""

    code = "tool_not_found"


class ToolValidationError(ToolError):
    """Raised when tool arguments fail schema validation."""

    code = "invalid_arguments"

    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"Invalid tool arguments: {errors}")


class ToolExecutionError(ToolError):
    """Raised when a tool fails while doing its work (DB error, etc.)."""

    code = "execution_failed"


class ToolUnauthorizedError(ToolError):
    """
    Raised when a user-scoped tool is called without a valid
    authenticated user in the ToolContext.
    """

    code = "unauthorized"