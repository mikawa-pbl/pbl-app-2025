from django import template
from django.contrib.auth import get_user_model

from ..models import AppAccount

register = template.Library()


@register.simple_tag
def user_points(user):
    """
    ログインユーザーに紐づくポイントを取得する。
    """
    if not user or not user.is_authenticated:
        return None
    account = (
        AppAccount.objects.using("h34vvy_u53rzz")
        .filter(app_code="h34vvy", user_id=user.id)
        .first()
    )
    return account.points if account else None
