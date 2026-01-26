from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime

class Tag(models.Model):
    # 例: "授業", "休講", "〇〇サークル", "A研究室", "授業名A" など
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        # 表示上は #を付けない（タグ名のみ）
        return self.name


class Post(models.Model):
    title = models.CharField("タイトル", max_length=100)
    # start/end are datetimes; if the event is all-day the time parts will be used in a conventional way
    start = models.DateTimeField("開始日時", null=True, blank=True)
    end = models.DateTimeField("終了日時", null=True, blank=True)

    body = models.TextField("本文", blank=True)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    # hashed edit-password (optional). 空ならパスワード保護なし
    password_hash = models.CharField("編集パスワード(ハッシュ)", max_length=128, blank=True, default="")

    # indicates whether this event is an all-day event (user did not set explicit times)
    all_day = models.BooleanField("終日", default=True)

    class Meta:
        ordering = ["start", "created_at"]  # start順に並べる

    def __str__(self):
        return self.title

    def set_password(self, raw_password):
        if raw_password:
            self.password_hash = make_password(raw_password)
        else:
            self.password_hash = ""

    def has_password(self):
        return bool(self.password_hash)

    def check_password(self, raw_password):
        """
        Return True if post is not password-protected or raw_password matches.
        """
        if not self.password_hash:
            return True
        if raw_password is None:
            return False
        return check_password(raw_password, self.password_hash)