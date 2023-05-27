from rest_framework import permissions


class IsAuthorAdminOrReadOnly(permissions.BasePermission):
    """Пермишн, является ли пользователь
    автором/суперпользователем/админом
    либо только GET-запросы."""
    message = 'У вас нет прав автора.'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_staff
                or obj.author == request.user)
