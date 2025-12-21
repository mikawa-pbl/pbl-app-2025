from django.contrib import admin
from .models import InvitationCode, Profile, Roadmap, ES

# 管理サイトで InvitationCode モデルを操作できるように登録
admin.site.register(InvitationCode)
admin.site.register(Profile)
admin.site.register(Roadmap)
admin.site.register(ES)