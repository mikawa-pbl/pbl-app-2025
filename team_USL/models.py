from django.db import models

class Floor(models.Model):
    class Meta:
        db_table = 'floor_table'
        # 既存テーブルを参照だけにしたい場合は↓を有効化
        # managed = False

    id = models.AutoField(primary_key=True)
    floor = models.IntegerField()
    url = models.TextField()  # フロア画像URL

    def __str__(self):
        return f"Floor {self.floor}"

class Room(models.Model):
    class Meta:
        db_table = 'room_table'
        # 既存テーブル参照だけなら↓
        # managed = False

    id = models.AutoField(primary_key=True)
    room_number = models.TextField()
    # floor_table と連携（物理名 building_id を維持）
    floor_fk = models.ForeignKey(
        Floor,
        on_delete=models.PROTECT,
        db_column='building_id',
        related_name='rooms'
    )
    x = models.FloatField()
    y = models.FloatField()
    created_dt = models.DateTimeField()
    updated_dt = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.room_number} (Floor {self.floor_fk.floor})"
