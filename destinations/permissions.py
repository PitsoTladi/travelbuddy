from rest_framework import permissions


class IsBusinessCreatorOwnerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):

        # Anyone authenticated can view destinations.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only Business Creators can create destinations.
        return request.user.role == 'business_creator'

    def has_object_permission(self, request, view, obj):

        # Anyone authenticated can view destinations.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only Business Creators can modify/delete
        # destinations they own.
        return (
            request.user.role == 'business_creator'
            and obj.created_by == request.user
        )