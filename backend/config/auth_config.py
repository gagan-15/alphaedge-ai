"""
Authentication configuration.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthConfig:
    """
    Secure token and cookie settings.
    """

    secret_key: str
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    algorithm: str = "HS256"
    refresh_cookie_name: str = "alphaedge_refresh"
    secure_cookies: bool = True

    @classmethod
    def from_environment(
        cls,
    ) -> "AuthConfig":
        """
        Load authentication settings from environment variables.
        """

        environment = os.getenv(
            "APP_ENV",
            "development",
        ).lower()

        return cls(
            secret_key=os.getenv(
                "AUTH_SECRET_KEY",
                "",
            ),
            access_token_minutes=int(
                os.getenv(
                    "ACCESS_TOKEN_MINUTES",
                    "15",
                )
            ),
            refresh_token_days=int(
                os.getenv(
                    "REFRESH_TOKEN_DAYS",
                    "7",
                )
            ),
            secure_cookies=environment != "development",
        )

    def validate(
        self,
    ) -> None:
        """
        Reject weak or invalid authentication settings.
        """

        if len(self.secret_key) < 32:
            raise ValueError(
                "AUTH_SECRET_KEY must contain at least 32 characters.",
            )

        if self.access_token_minutes <= 0:
            raise ValueError(
                "access_token_minutes must be greater than zero.",
            )

        if self.refresh_token_days <= 0:
            raise ValueError(
                "refresh_token_days must be greater than zero.",
            )
