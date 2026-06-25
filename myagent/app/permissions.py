from typing import List


def is_allowed(permission: str, permissions: List[str] | None) -> bool:
    if not permissions:
        return False
    return permission in permissions


