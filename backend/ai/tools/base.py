import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import DatabaseError

from .errors import ToolExecutionError, ToolValidationError

logger = logging.getLogger(__name__)


class BaseTool:
    """
    Base class for all MCP/AI domain tools.

    Subclasses set:
      - name: unique tool name (str)
      - description: short human/AI-readable description
      - input_serializer_class: a DRF Serializer used both to validate
        arguments and to advertise the tool's input schema for discovery
      - requires_user_context: True if the tool needs an authenticated
        user (see ToolContext / ToolRegistry.call)

    Subclasses implement `run(validated_args, context) -> dict`, which
    should call into existing Django domain services rather than
    duplicating ORM/business logic.
    """

    name = None
    description = ""
    input_serializer_class = None
    requires_user_context = False

    def get_schema(self):
        """Discovery metadata describing this tool's name/purpose/inputs."""
        fields = {}
        if self.input_serializer_class:
            for field_name, field in self.input_serializer_class().fields.items():
                fields[field_name] = {
                    "type": type(field).__name__,
                    "required": field.required,
                }
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": fields,
            "requires_user_context": self.requires_user_context,
        }

    def validate(self, arguments):
        if not self.input_serializer_class:
            return arguments or {}
        serializer = self.input_serializer_class(data=arguments or {})
        if not serializer.is_valid():
            raise ToolValidationError(serializer.errors)
        return serializer.validated_data

    def run(self, validated_args, context):
        raise NotImplementedError

    def __call__(self, arguments, context):
        validated = self.validate(arguments)
        try:
            return self.run(validated, context)
        except ToolExecutionError:
            raise
        except (DatabaseError, DjangoValidationError) as exc:
            logger.error("Tool '%s' database error: %s", self.name, exc)
            raise ToolExecutionError(
                f"{self.name} failed due to a database error."
            ) from exc
        except Exception as exc:  # noqa: BLE001 - last line of defense
            logger.exception("Tool '%s' unexpected error", self.name)
            raise ToolExecutionError(f"{self.name} failed unexpectedly.") from exc