import uuid
from django.db import models

class Good(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    # store only the filename of image saved under templates/teams/team_cake/images/
    image_filename = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    original_price = models.IntegerField(blank=True, null=True)
    expiration_time = models.DateTimeField(blank=True, null=True, verbose_name="賞味期限(廃棄予定時刻)")

    def __str__(self):
        return f"{self.name} {self.price}"

class SOSMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField(verbose_name="助けてメッセージ")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="表示中")

    def __str__(self):
        return self.message[:20]