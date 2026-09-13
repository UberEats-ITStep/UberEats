import sys

from django.core.checks import Error, Tags, register
from django.db import connection
from django.db.utils import DatabaseError


@register(Tags.database)
def check_postgresql_connection(app_configs, **kwargs):
    """Confirm the database connection after Django finishes app setup."""
    if sys.argv[1:2] != ["runserver"]:
        return []

    database_config = connection.settings_dict
    engine = database_config.get("ENGINE", "")
    host = database_config.get("HOST") or "localhost"

    if "postgresql" not in engine:
        print(
            "⚠️  Database diagnostic: PostgreSQL is not configured "
            f"(engine: {engine or 'unknown'})."
        )
        return []

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError as error:
        print(
            "❌ PostgreSQL database connection failed: "
            f"{error.__class__.__name__}: {error}"
        )
        return [
            Error(
                "The configured PostgreSQL database is not reachable.",
                hint="Check the PostgreSQL host, credentials, and network access.",
                id="database.E001",
            )
        ]

    is_local = host in {"localhost", "127.0.0.1", "::1"}
    location = "local" if is_local else "hosted"
    emoji = "💻" if is_local else "☁️"
    print(f"{emoji} ✅ PostgreSQL {location} database connected successfully!")
    print(f"   🗄️  Database host: {host}")
    return []
