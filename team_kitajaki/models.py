from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

# ★ 追加：メニュー評価を保存するモデル
class MenuRating(models.Model):
    # メニューを一意に識別するための文字列（例: "厚旨トンカツ"）。PDFのメニュー行がキーとなる。
    menu_name = models.CharField(max_length=255)
    # 評価日
    rating_date = models.DateField(auto_now_add=True) 
    # 味の評価 (1〜5)
    taste_score = models.IntegerField()
    # 量の評価 (1〜5)
    volume_score = models.IntegerField()
    
    def __str__(self):
        return f"Rating for {self.menu_name} - Taste: {self.taste_score}, Volume: {self.volume_score}"