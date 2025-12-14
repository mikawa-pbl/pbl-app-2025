from __future__ import annotations

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden

from routers import TeamPerAppRouter


class TeamPrefixAuthorizationMiddleware:
    """
    URLプレフィックスによるアプリ単位のアクセス制御。

    パス先頭のセグメントが保護対象の app_label（例: /team_USL/...）に一致した場合に、
    次を要求する:
      - ログイン済みであること
      - 同名の Group に所属していること（または superuser）

    認証テーブルは default DB に置いたまま、ここでは Group 所属だけをチェックする。
    """

    def __init__(self, get_response):
        self.get_response = get_response
        configured = getattr(settings, "TEAM_AUTHZ_PROTECTED_APP_LABELS", None)
        if configured is None:
            self._protected_app_labels = set(TeamPerAppRouter.app_to_db.keys())
        else:
            self._protected_app_labels = set(configured)
        self._exempt_prefixes = tuple(
            getattr(settings, "TEAM_AUTHZ_EXEMPT_PREFIXES", ["/"])
        )

    def __call__(self, request):
        path = request.path_info or "/"
        if path == "/":
            return self.get_response(request)
        if any(path.startswith(prefix) for prefix in self._exempt_prefixes):
            return self.get_response(request)

        first_segment = path.lstrip("/").split("/", 1)[0]
        if first_segment and first_segment in self._protected_app_labels:
            user = getattr(request, "user", None)
            if not user or not user.is_authenticated:
                return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
            if user.is_superuser:
                return self.get_response(request)
            if user.groups.filter(name=first_segment).exists():
                return self.get_response(request)
            return HttpResponseForbidden("Forbidden")

        return self.get_response(request)
