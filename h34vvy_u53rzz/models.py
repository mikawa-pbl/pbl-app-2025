from django.db import models

from .doors import DOORS


DOOR_LABEL_MAP = {door.id: door.label for door in DOORS}


class AppAccount(models.Model):
    """
    default DB の auth_user（共有）と、アプリ内のローカルユーザー名を紐づける。
    FKを張るとDBが跨ってしまうため、user_idは整数で保持する。
    """

    app_code = models.CharField(max_length=64, default="h34vvy", db_index=True)
    local_username = models.CharField(max_length=150)
    user_id = models.PositiveIntegerField(help_text="auth_user.id")
    points = models.PositiveIntegerField(default=0, help_text="アプリ内ポイント")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("app_code", "local_username")
        indexes = [
            models.Index(fields=["app_code", "local_username"]),
        ]

    def __str__(self):
        return f"{self.app_code}:{self.local_username} -> {self.user_id}"


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
