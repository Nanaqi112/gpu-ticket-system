from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    管理员可读写，普通用户只读
    """
    def has_permission(self, request, view):
        # 读取权限允许任何已认证用户
        if request.method in permissions.SAFE_METHODS:
            return True
        # 写入权限只允许管理员
        return request.user and request.user.is_staff