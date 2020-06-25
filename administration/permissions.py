from rest_framework.permissions import BasePermission


class IsAuthenticatedToRead(BasePermission):
    """
    The request to create or from admin to read.
    """

    def has_permission(self, request, view):
        return request.method == 'POST' or (
                request.user and request.user.is_staff
        )
