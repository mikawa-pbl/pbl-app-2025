from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class MenuRating(models.Model):
    menu_name = models.CharField(max_length=255)

    # 既存
    rating_date = models.DateField(auto_now_add=True)
    taste_score = models.IntegerField()
    volume_score = models.IntegerField()

    # ★追加：コメント（任意）
    comment = models.TextField(blank=True, default="")

    # ★追加：投稿日時（Amazonっぽく並べ替え用）
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Rating for {self.menu_name} - Taste: {self.taste_score}, Volume: {self.volume_score}"
