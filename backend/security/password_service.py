"""
Secure password hashing service.
"""

from pwdlib import PasswordHash


class PasswordService:
    """
    Hash and verify passwords using Argon2.
    """

    def __init__(
        self,
    ) -> None:
        self._password_hash = PasswordHash.recommended()

    def hash_password(
        self,
        password: str,
    ) -> str:
        """
        Hash a valid user password.
        """

        self._validate_password(
            password,
        )

        return self._password_hash.hash(
            password,
        )

    def verify_password(
        self,
        password: str,
        password_hash: str,
    ) -> bool:
        """
        Safely compare a password with its stored hash.
        """

        if not password or not password_hash:
            return False

        return self._password_hash.verify(
            password,
            password_hash,
        )

    @staticmethod
    def _validate_password(
        password: str,
    ) -> None:
        """
        Apply the minimum account password policy.
        """

        if len(password) < 12:
            raise ValueError(
                "Password must contain at least 12 characters.",
            )

        if not any(character.isupper() for character in password):
            raise ValueError(
                "Password must contain an uppercase letter.",
            )

        if not any(character.islower() for character in password):
            raise ValueError(
                "Password must contain a lowercase letter.",
            )

        if not any(character.isdigit() for character in password):
            raise ValueError(
                "Password must contain a number.",
            )

        if password.isalnum():
            raise ValueError(
                "Password must contain a special character.",
            )
