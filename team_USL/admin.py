from django.contrib import admin
from .models import Floor, Room

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('id', 'floor', 'url')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'room_number', 'floor_fk', 'x', 'y', 'is_deleted')
    list_filter = ('floor_fk', 'is_deleted')
    search_fields = ('room_number',)
