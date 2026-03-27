from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsJournalistOrReadOnly(BasePermission):
    """
    Allow everyone to read articles, but only journalists and editors can create them.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user.is_authenticated
            and getattr(request.user, "role", None) in {"journalist", "editor"}
        )


class IsEditor(BasePermission):
    """
    Editors can approve content and access editor-only endpoints.
    """

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "editor"
        )