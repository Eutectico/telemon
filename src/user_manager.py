"""User authorization and management."""

import json
from pathlib import Path
from typing import Set
from loguru import logger


class UserManager:
    """Manages authorized users for the Telegram bot."""

    def __init__(self, authorized_users: list, storage_path: str = "data/authorized_users.json"):
        """Initialize user manager.

        Args:
            authorized_users: Initial list of authorized user IDs
            storage_path: Path to store authorized users
        """
        self.storage_path = Path(storage_path)
        self.authorized_users: Set[int] = set(authorized_users)

        # Create data directory if it doesn't exist
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Load additional users from storage
        self._load_users()

    def _load_users(self):
        """Load authorized users from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    stored_users = json.load(f)
                    self.authorized_users.update(stored_users)
                logger.info(f"Loaded {len(stored_users)} users from storage")
            except Exception as e:
                logger.error(f"Failed to load users from storage: {e}")

    def _save_users(self):
        """Save authorized users to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(list(self.authorized_users), f, indent=2)
            logger.info(f"Saved {len(self.authorized_users)} users to storage")
        except Exception as e:
            logger.error(f"Failed to save users to storage: {e}")

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user is authorized, False otherwise
        """
        return user_id in self.authorized_users

    def add_user(self, user_id: int) -> bool:
        """Add user to authorized list.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user was added, False if already exists
        """
        if user_id in self.authorized_users:
            return False

        self.authorized_users.add(user_id)
        self._save_users()
        logger.info(f"Added user {user_id} to authorized list")
        return True

    def remove_user(self, user_id: int) -> bool:
        """Remove user from authorized list.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user was removed, False if not found
        """
        if user_id not in self.authorized_users:
            return False

        self.authorized_users.remove(user_id)
        self._save_users()
        logger.info(f"Removed user {user_id} from authorized list")
        return True

    def get_all_users(self) -> list:
        """Get list of all authorized users.

        Returns:
            List of authorized user IDs
        """
        return list(self.authorized_users)
