from django.db import models
from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Entry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField()

    class Meta:
        ordering = ["-created_at"]  # 新しい順で積み上げ表示

    def __str__(self):
        # 管理画面用
        return f"{self.created_at:%Y-%m-%d %H:%M:%S} {self.body[:20]}"
