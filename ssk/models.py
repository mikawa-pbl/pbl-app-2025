from django.db import models

class Tag(models.Model):
    # 例: "授業", "休講", "〇〇サークル", "A研究室", "授業名A" など
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        # 表示上は #を付けたいならここで
        return f"#{self.name}"


class Post(models.Model):
    title = models.CharField("タイトル", max_length=100)
    date = models.DateField("イベント日")  # 掲示板に並べる基準の日付
    body = models.TextField("本文", blank=True)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "created_at"]  # 日付順に並べる

    def __str__(self):
        return self.title