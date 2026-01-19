from django.db import models


class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class FloorTable(models.Model):
    # floor_table
    floor = models.TextField(unique=True)
    url = models.TextField()  # 例: "images/A-3.png" や "/team_USL/images/A-3.png"

    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Floor {self.floor}"

    class Meta:
        db_table = "floor_table"


class RoomTable(models.Model):
    # room_table
    room_number = models.TextField()
    building_id = models.CharField(max_length=50)  # A案： "A" など文字で保持

    x = models.FloatField()
    y = models.FloatField()

    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.building_id}-{self.room_number}"

    class Meta:
        db_table = "room_table"
        indexes = [
            models.Index(fields=["building_id", "room_number", "is_deleted"]),
        ]

class FloorRange(models.Model):
    # building_floor_range テーブル
    building_name = models.TextField(unique=True) # 棟の名前 (ex. A, A1, B)
    min_floor = models.IntegerField()              # 最低階 (通常は 1)
    max_floor = models.IntegerField()              # 最高階

    def __str__(self):
        return f"{self.building_name}: {self.min_floor}F - {self.max_floor}F"

    class Meta:
        db_table = "building_floor_range"