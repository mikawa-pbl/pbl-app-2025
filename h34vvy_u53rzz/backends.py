from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db import connections
from django.db.utils import DatabaseError

from .models import AppAccount


class H34vvyBackend(BaseBackend):
    """
    アプリ固有のローカルユーザー名を auth_user（default DB）にひも付けるバックエンド。
    """

    app_code = "h34vvy"

    def authenticate(self, request, username=None, password=None, app_code=None, **kwargs):
        # username: ローカルユーザー名
        if username is None or password is None:
            return None
        target_app = app_code or self.app_code
        try:
            account = AppAccount.objects.using("h34vvy_u53rzz").get(
                app_code=target_app, local_username=username
            )
        except AppAccount.DoesNotExist:
            return None

        UserModel = get_user_model()
        try:
            user = UserModel.objects.using("default").get(pk=account.user_id)
        except UserModel.DoesNotExist:
            return None
        except DatabaseError:
            # default DB に接続できないなどの場合は認証不可
            return None

        if not user.is_active:
            return None
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.using("default").get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
