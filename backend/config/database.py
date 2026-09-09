from os import environ
from urllib.parse import parse_qs, unquote, urlparse


class DatabaseConfigurationError(ValueError):
    """Raised when DATABASE_URL is not a valid PostgreSQL connection URL."""


def database_config_from_environment(environment=None):
    """Return a Django PostgreSQL config from DATABASE_URL or POSTGRES_* values."""
    environment = environment or environ
    database_url = environment.get("DATABASE_URL")

    if database_url:
        parsed = urlparse(database_url)
        if parsed.scheme not in {"postgres", "postgresql"}:
            raise DatabaseConfigurationError(
                "DATABASE_URL must use the postgres or postgresql scheme."
            )
        if not parsed.hostname or not parsed.path or parsed.path == "/":
            raise DatabaseConfigurationError(
                "DATABASE_URL must include a host and database name."
            )
        try:
            port = parsed.port or 5432
        except ValueError as error:
            raise DatabaseConfigurationError(
                "DATABASE_URL has an invalid port."
            ) from error

        options = {
            key: values[-1]
            for key, values in parse_qs(parsed.query).items()
            if values
        }
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(parsed.path.lstrip("/")),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname,
            "PORT": str(port),
            "OPTIONS": options,
        }

    required_variables = (
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
    )
    missing_variables = [
        variable for variable in required_variables if not environment.get(variable)
    ]
    if missing_variables:
        raise DatabaseConfigurationError(
            "Set DATABASE_URL or the required PostgreSQL variables: "
            + ", ".join(missing_variables)
            + "."
        )

    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": environment["POSTGRES_DB"],
        "USER": environment["POSTGRES_USER"],
        "PASSWORD": environment["POSTGRES_PASSWORD"],
        "HOST": environment["POSTGRES_HOST"],
        "PORT": environment["POSTGRES_PORT"],
        "OPTIONS": {
            "sslmode": environment["POSTGRES_SSLMODE"],
        },
    }


def add_connection_safety(database_config, environment=None):
    """Apply safe defaults for serverless PostgreSQL connections such as Neon."""
    environment = environment or environ
    database_config.update(
        {
            "CONN_MAX_AGE": int(environment["DATABASE_CONN_MAX_AGE"]),
            "CONN_HEALTH_CHECKS": True,
            "DISABLE_SERVER_SIDE_CURSORS": True,
        }
    )
    return database_config