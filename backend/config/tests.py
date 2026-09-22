from django.test import SimpleTestCase

from .database import DatabaseConfigurationError, add_connection_safety, database_config_from_environment


class DatabaseConfigurationTests(SimpleTestCase):
    def test_database_url_takes_priority_and_preserves_tls_options(self):
        config = database_config_from_environment(
            {
                "DATABASE_URL": (
                    "postgresql://catalog_user:secret@ep-example.neon.tech:5432/"
                    "neondb?sslmode=require&channel_binding=require"
                ),
                "POSTGRES_DB": "ignored",
            }
        )
        config = add_connection_safety(config, {"DATABASE_CONN_MAX_AGE": "60"})

        self.assertEqual(config["NAME"], "neondb")
        self.assertEqual(config["USER"], "catalog_user")
        self.assertEqual(config["HOST"], "ep-example.neon.tech")
        self.assertEqual(config["OPTIONS"]["sslmode"], "require")
        self.assertEqual(config["OPTIONS"]["channel_binding"], "require")
        self.assertEqual(config["CONN_MAX_AGE"], 60)
        self.assertTrue(config["CONN_HEALTH_CHECKS"])

    def test_postgres_variables_are_the_local_development_fallback(self):
        config = database_config_from_environment(
            {
                "POSTGRES_DB": "ubereats",
                "POSTGRES_USER": "local_user",
                "POSTGRES_PASSWORD": "local_password",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5433",
                "POSTGRES_SSLMODE": "prefer",
            }
        )

        self.assertEqual(config["NAME"], "ubereats")
        self.assertEqual(config["PORT"], "5433")
        self.assertEqual(config["OPTIONS"]["sslmode"], "prefer")

    def test_non_postgres_database_url_is_rejected(self):
        with self.assertRaises(DatabaseConfigurationError):
            database_config_from_environment({"DATABASE_URL": "sqlite:///db.sqlite3"})

    def test_missing_local_credentials_are_rejected(self):
        with self.assertRaisesRegex(
            DatabaseConfigurationError,
            "Set DATABASE_URL or the required PostgreSQL variables",
        ):
            database_config_from_environment({"POSTGRES_DB": "ubereats"})

    def test_connection_safety_has_serverless_default(self):
        config = add_connection_safety({}, {})

        self.assertEqual(config["CONN_MAX_AGE"], 0)
        self.assertTrue(config["CONN_HEALTH_CHECKS"])
        self.assertTrue(config["DISABLE_SERVER_SIDE_CURSORS"])

    def test_invalid_connection_max_age_is_rejected(self):
        with self.assertRaisesRegex(
            DatabaseConfigurationError, "DATABASE_CONN_MAX_AGE must be an integer"
        ):
            add_connection_safety({}, {"DATABASE_CONN_MAX_AGE": "forever"})
