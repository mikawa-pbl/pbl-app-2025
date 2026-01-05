from django.contrib import admin
from .models import Member, MenuRating # ★ MenuRating をインポート

# Register your models here.
admin.site.register(Member)
admin.site.register(MenuRating) # ★ MenuRating を登録