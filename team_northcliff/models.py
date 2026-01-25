from django.db import models


class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class User(models.Model):
    name = models.CharField(max_length=100, verbose_name="ユーザー名")
    points = models.IntegerField(default=10, verbose_name="保有ポイント")
    latitude = models.FloatField(blank=True, null=True, verbose_name="緯度")
    longitude = models.FloatField(blank=True, null=True, verbose_name="経度")

    def __str__(self):
        return f"{self.name} ({self.points}P)"

    class Meta:
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー"


class Facility(models.Model):
    FACILITY_CHOICES = [
        ("lib", "🏢 図書館"),
        ("hiba", "🍴 食堂（ひばり）"),
        ("kita", "🅿️ 北駐車場"),
        #("cafe", "☕️ カフェ"),
        ("bus", "🚌 バス停"),
        ("gym", "🏋️ ジム"),
    ]

    facility_id = models.CharField(max_length=10, unique=True, choices=FACILITY_CHOICES)
    name = models.CharField(max_length=100, verbose_name="施設名")
    latitude = models.FloatField(blank=True, null=True, verbose_name="緯度")
    longitude = models.FloatField(blank=True, null=True, verbose_name="経度")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "施設"
        verbose_name_plural = "施設"


class Post(models.Model):
    STATUS_CHOICES = [
        ("empty", "🟢 空いている"),
        ("moderate", "🟡 やや混雑"),
        ("crowded", "🔴 混雑"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", verbose_name="投稿者"
    )
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="posts", verbose_name="施設"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="混雑状況"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="コメント")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="投稿日時")

    def __str__(self):
        return f"{self.facility.name} - {self.status} ({self.created_at})"

    class Meta:
        verbose_name = "投稿"
        verbose_name_plural = "投稿"
        ordering = ["-created_at"]


class FacilityAccess(models.Model):
    """ユーザーが施設情報を閲覧したかどうかを追跡"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="facility_accesses",
        verbose_name="ユーザー",
    )
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="accesses", verbose_name="施設"
    )
    accessed_at = models.DateTimeField(auto_now=True, verbose_name="閲覧日時")

    class Meta:
        unique_together = ("user", "facility")
        verbose_name = "施設閲覧履歴"
        verbose_name_plural = "施設閲覧履歴"

    def __str__(self):
        return f"{self.user.name} - {self.facility.name}"
