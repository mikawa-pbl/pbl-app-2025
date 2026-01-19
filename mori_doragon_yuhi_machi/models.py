from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

STATIC_IMAGES_PATH = settings.BASE_DIR / 'mori_doragon_yuhi_machi' / 'static' / 'images'

static_storage = FileSystemStorage(
    location=STATIC_IMAGES_PATH,
    base_url='/static/images/'
)

class Place(models.Model):
    name = models.CharField("場所の名前", max_length=100, unique=True) # 場所名は重複しないように unique=True を推奨

    def __str__(self):
        return self.name

class Member(models.Model):
    name = models.CharField("メンバー名", max_length=100)

    photo = models.ImageField(
        "顔写真",
        storage=static_storage,  # ここで保存先を指定
        upload_to='',            # サブフォルダは作らない
        null=True,
        blank=True
    )
    
    # MemberモデルとPlaceモデルを「多対一」で関連付ける
    current_place = models.ForeignKey(
        Place,
        verbose_name="現在の居場所",
        on_delete=models.SET_NULL, # 場所がDBから削除されても、メンバーは削除しない (SET_NULL = 居場所をNULLにする)
        null=True,                 # DB上でNULL (どこにもいない状態) を許可
        blank=True                 # 管理画面などで空欄を許可
    )

    def __str__(self):
        return self.name
