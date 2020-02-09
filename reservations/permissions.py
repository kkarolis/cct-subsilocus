from rest_framework import permissions


# based on https://www.django-rest-framework.org/api-guide/permissions/#examples
class IsOwner(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to interact with it."""

    # pylint: disable=no-self-use,unused-argument
    def has_object_permission(self, request, view, obj):
        # Instance must have an attribute named `owner`.
        return obj.owner == request.user
