from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolContext:
    """
    Carries the authenticated request context into a tool call.

    User isolation rule: user-scoped tools MUST read the user from
    `context.user`, never from a `user_id`-style argument supplied by
    the model. Tool input schemas for user-scoped tools should not
    even define a user id field, so there is no argument for a
    misbehaving or manipulated model to exploit.
    """

    user: Any
    request_id: str = ""