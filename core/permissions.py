from rest_framework.permissions import BasePermission


class IsApprovedOperator(BasePermission):
    """Allow access only to approved operator accounts."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, 'is_operator', False)
            and getattr(user, 'is_active', False)
            and getattr(user, 'is_approved', True)
        )

