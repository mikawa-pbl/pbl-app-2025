from django.contrib import admin
from .models import Event, Memo, QuestionAnswer


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


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ("account", "company", "question", "has_answer", "updated_at")
    list_filter = ("company", "created_at")
    search_fields = ("question", "answer")
    
    def has_answer(self, obj):
        return bool(obj.answer)
    has_answer.boolean = True
    has_answer.short_description = "回答済み"
