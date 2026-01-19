from django.contrib import admin
from .models import Good, SOSMessage

class GoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'original_price')

class SOSMessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at', 'is_active')
    list_filter = ('is_active',)

admin.site.register(Good, GoodAdmin)
admin.site.register(SOSMessage, SOSMessageAdmin)
