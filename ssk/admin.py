from django.contrib import admin
from .models import Tag, Post

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "start_time", "end_time", "created_at")
    list_filter = ("date", "start_time", "end_time", "tags")
    search_fields = ("title", "body")
