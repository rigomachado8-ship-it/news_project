from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsJournalistOrReadOnly(BasePermission):
    """
    Read access for everyone.
    Write/create access only for authenticated journalists.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user.is_authenticated
            and getattr(request.user, "is_journalist", False)
        )


class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated and getattr(request.user, "is_editor", False)
        )
