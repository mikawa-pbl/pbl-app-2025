from django import template

from ..models import H34vvyUser

register = template.Library()


@register.simple_tag
def user_points(user):
    """
    ログインユーザーに紐づくポイントを取得する。
    """
    if not user or not user.is_authenticated:
        return None
    account = H34vvyUser.objects.filter(id=user.id).first()
    return account.points if account else None
