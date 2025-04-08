from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Кастомна перевірка, яка дозволяє доступ тільки для адміністраторів.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Дозволяє редагувати об'єкт тільки власнику, але переглядати можуть всі.
    """

    def has_object_permission(self, request, view, obj):
        # Дозволяємо GET, HEAD та OPTIONS запити
        if request.method in permissions.SAFE_METHODS:
            return True

        # Перевіряємо, чи є поле user в об'єкті
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False