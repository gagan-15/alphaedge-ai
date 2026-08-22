"""
Database configuration.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseConfig:
    """
    PostgreSQL connection settings.
    """

    url: str
    echo: bool = False

    @classmethod
    def from_environment(
        cls,
    ) -> "DatabaseConfig":
        return cls(
            url=os.getenv(
                "DATABASE_URL",
                "",
            ),
            echo=os.getenv(
                "DATABASE_ECHO",
                "false",
            ).lower()
            == "true",
        )

    def validate(
        self,
    ) -> None:
        if not self.url:
            raise ValueError(
                "DATABASE_URL is required.",
            )

        if not (
            self.url.startswith("postgresql+psycopg://")
            or self.url.startswith("sqlite")
        ):
            raise ValueError(
                "DATABASE_URL must use PostgreSQL or isolated SQLite tests.",
            )
