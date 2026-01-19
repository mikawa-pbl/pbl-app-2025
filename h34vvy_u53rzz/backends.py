from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore

from .models import H34vvyUser


class H34vvySessionStore(SessionStore):
    """
    チーム独自のセッションストレージ
    """

    @classmethod
    def get_model_class(cls):
        # Avoids a circular import and allows importing SessionStore when
        # django.contrib.sessions is not in INSTALLED_APPS.
        from .models import H34vvySession

        return H34vvySession


def is_h34vvy_u53rzz_request(request) -> bool:
    if request is None:
        return False
    return request.path.startswith("/h34vvy_u53rzz/")


class H34vvyUserBackend(BaseBackend):
    """
    チーム独自の認証ユーザバックエンド
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 対象外のアプリなら None を返して次の認証バックエンドに素通りさせる
        if not is_h34vvy_u53rzz_request(request):
            return None
        # 以降、認証できなかったら AnonymousUser() を返して認証プロセスを終了する

        if username is None or password is None:
            return AnonymousUser()
        try:
            user = H34vvyUser.objects.get(username=username)
        except H34vvyUser.DoesNotExist:
            return AnonymousUser()

        if not user.is_active:
            return AnonymousUser()
        if user.check_password(password):
            return user
        return AnonymousUser()

    def get_user(self, user_id):
        try:
            return H34vvyUser.objects.get(pk=user_id)
        except H34vvyUser.DoesNotExist:
            pass
        return None
