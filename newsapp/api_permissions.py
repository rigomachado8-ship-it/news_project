from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsJournalistOrReadOnly(BasePermission):
    """
    Allow anyone to read articles.
    Only journalists or editors can create/update article content.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user.is_authenticated
            and (
                getattr(request.user, "is_journalist", False)
                or getattr(request.user, "is_editor", False)
            )
        )


class IsEditor(BasePermission):
    """Allow editors only."""

    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and getattr(request.user, "is_editor", False)
        )


class IsOwnerOrEditor(BasePermission):
    """Allow profile owners or editors."""

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.is_authenticated
            and (
                request.user == obj
                or getattr(request.user, "is_editor", False)
            )
        )