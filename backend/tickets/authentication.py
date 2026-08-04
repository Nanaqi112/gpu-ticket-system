from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    自定义SessionAuthentication，豁免CSRF检查
    用于登录/登出等不需要CSRF验证的接口
    """
    def enforce_csrf(self, request):
        return  # 跳过CSRF验证
