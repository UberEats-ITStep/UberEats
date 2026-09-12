import logging

from .errors import ToolNotFoundError, ToolUnauthorizedError

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry the AI/orchestrator uses to discover and call
    domain tools. This is the "MCP layer" seam: swapping the transport
    (in-process registry today, an actual MCP server later) shouldn't
    require touching tool implementations.
    """

    def __init__(self):
        self._tools = {}

    def register(self, tool):
        if not tool.name:
            raise ValueError("Tool must define a 'name'.")
        self._tools[tool.name] = tool
        return tool

    def get(self, name):
        try:
            return self._tools[name]
        except KeyError:
            raise ToolNotFoundError(f"Unknown tool: {name}")

    def list_tools(self):
        """Tool discovery: schema metadata for every registered tool."""
        return [tool.get_schema() for tool in self._tools.values()]

    def call(self, name, arguments=None, context=None):
        """
        Validate + invoke a tool by name, enforcing user-context
        requirements before execution. Returns a structured envelope;
        raises a ToolError subclass on failure.
        """
        tool = self.get(name)

        if tool.requires_user_context and (context is None or context.user is None):
            raise ToolUnauthorizedError(
                f"Tool '{name}' requires an authenticated user context."
            )

        logger.info("Calling tool '%s' args=%s", name, arguments)
        result = tool(arguments or {}, context)
        return {"tool": name, "success": True, "data": result}


registry = ToolRegistry()