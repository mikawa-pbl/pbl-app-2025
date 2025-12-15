from django.contrib import admin
from .models import Event, Memo


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_time", "end_time")
    list_filter = ("start_time", "end_time")
    search_fields = ("title",)


@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = ("content", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("content",)
