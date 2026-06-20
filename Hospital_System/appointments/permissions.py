from rest_framework import permissions


class IsAdminOrCreateOnly(permissions.BasePermission):
    """Anyone may create (book); only staff may list/inspect submissions."""

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return bool(request.user and request.user.is_staff)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Read for everyone; write only for staff."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
