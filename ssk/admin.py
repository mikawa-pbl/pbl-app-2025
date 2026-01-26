from django.contrib import admin
from .models import Tag, Post

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "start", "end", "created_at")
    list_filter = ("start", "end", "tags")
    search_fields = ("title", "body")
