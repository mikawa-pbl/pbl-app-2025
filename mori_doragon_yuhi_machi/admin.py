# mori_doragon_yuhi_machi/admin.py
from django.contrib import admin
from .models import Member, Place # モデルをインポート

# 管理サイトに登録
admin.site.register(Member)
admin.site.register(Place)