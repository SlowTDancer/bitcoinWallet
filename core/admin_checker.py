from uuid import UUID

from constants import ADMIN_API_KEY
from core.errors import InvalidAdminAPIKeyError


def check_admin(api_key: UUID) -> bool:
    if api_key == ADMIN_API_KEY:
        return True

    raise InvalidAdminAPIKeyError(api_key)
