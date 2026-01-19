from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.sessions.base_session import AbstractBaseSession
from django.contrib.sessions.models import SessionManager
from django.db import models

from .doors import DOORS
from .labs import LABORATORIES



DOOR_LABEL_MAP = {door.id: door.label for door in DOORS}
LAB_LABEL_MAP = {lab.id: lab.name for lab in LABORATORIES}


class H34vvySession(AbstractBaseSession):
    """
    チーム独自のセッションDB
    """

    objects = SessionManager()

    @classmethod
    def get_session_store_class(cls):
        from .backends import SessionStore

        return SessionStore


class H34vvyGroup(Group):
    pass


class H34vvyPermission(Permission):
    pass




class H34vvyUser(AbstractUser):
    """
    チーム独自の認証・認可用ユーザアカウント
    """

    points = models.PositiveIntegerField(default=0, help_text="アプリ内ポイント")
    laboratory = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="所属研究室ID",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # auth.models.PermissionsMixin で定義されている外部キーが
    # 共有テーブルではなくチーム固有のテーブルを参照するように変更する
    groups = models.ManyToManyField(
        H34vvyGroup,
        blank=True,
        related_name="h34vvy_user_set",
        related_query_name="h34vvy_user",
    )
    user_permissions = models.ManyToManyField(
        H34vvyPermission,
        blank=True,
        related_name="h34vvy_user_set",
        related_query_name="h34vvy_user",
    )

    @property
    def lab_label(self) -> str:
        if not self.laboratory:
            return "未所属"
        return LAB_LABEL_MAP.get(self.laboratory, self.laboratory)


# 後でなくす
class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Entry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    door_id = models.CharField(max_length=64, blank=True, help_text="対応したドアID")
    comment = models.TextField(blank=True, help_text="ドアに関する任意コメント")
    helper_confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="ヘルパーが応答した日時",
    )

    class Meta:
        ordering = ["-created_at"]  # 新しい順で積み上げ表示

    def __str__(self):
        # 管理画面用
        preview = (self.comment or "")[:20]
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} {preview}"

    @property
    def door_label(self) -> str:
        if not self.door_id:
            return "ドア未指定"
        return DOOR_LABEL_MAP.get(self.door_id, self.door_id)
