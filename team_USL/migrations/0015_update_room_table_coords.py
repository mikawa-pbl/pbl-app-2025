from django.db import migrations

SQL_MIGRATE = """
UPDATE room_table SET x = 85, y = 68, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '105' AND is_deleted = 0;
UPDATE room_table SET x = 85, y = 53, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '106' AND is_deleted = 0;
UPDATE room_table SET x = 78, y = 40, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '108' AND is_deleted = 0;
UPDATE room_table SET x = 64, y = 40, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '109' AND is_deleted = 0;
UPDATE room_table SET x = 52, y = 40, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '110' AND is_deleted = 0;
UPDATE room_table SET x = 40, y = 40, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '111' AND is_deleted = 0;
UPDATE room_table SET x = 50, y = 85, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '114' AND is_deleted = 0;
UPDATE room_table SET x = 81, y = 70, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '201' AND is_deleted = 0;
UPDATE room_table SET x = 81, y = 60, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '202' AND is_deleted = 0;
UPDATE room_table SET x = 81, y = 52, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '203' AND is_deleted = 0;
UPDATE room_table SET x = 70, y = 40, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '205' AND is_deleted = 0;
UPDATE room_table SET x = 52, y = 40, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '207' AND is_deleted = 0;
UPDATE room_table SET x = 40, y = 40, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '208' AND is_deleted = 0;
UPDATE room_table SET x = 25, y = 40, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '209' AND is_deleted = 0;
UPDATE room_table SET x = 20, y = 14, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A1' AND room_number = '201' AND is_deleted = 0;
UPDATE room_table SET x = 58, y = 18, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A2' AND room_number = '201' AND is_deleted = 0;
UPDATE room_table SET x = 81, y = 72, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '301' AND is_deleted = 0;
UPDATE room_table SET x = 81, y = 63, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '302' AND is_deleted = 0;
UPDATE room_table SET x = 81, y = 55, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '303' AND is_deleted = 0;
UPDATE room_table SET x = 81, y = 35, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '304' AND is_deleted = 0;
UPDATE room_table SET x = 70, y = 41, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '306' AND is_deleted = 0;
UPDATE room_table SET x = 60, y = 41, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '307' AND is_deleted = 0;
UPDATE room_table SET x = 52, y = 41, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '308' AND is_deleted = 0;
UPDATE room_table SET x = 40, y = 41, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '309' AND is_deleted = 0;
UPDATE room_table SET x = 25, y = 41, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '311' AND is_deleted = 0;
UPDATE room_table SET x = 70, y = 60, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '312' AND is_deleted = 0;
UPDATE room_table SET x = 27, y = 14, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A1' AND room_number = '101' AND is_deleted = 0;
UPDATE room_table SET x = 27, y = 14, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A1' AND room_number = '201' AND is_deleted = 0;
UPDATE room_table SET x = 27, y = 14, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A1' AND room_number = '301' AND is_deleted = 0;
UPDATE room_table SET x = 58, y = 16, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A2' AND room_number = '101' AND is_deleted = 0;
UPDATE room_table SET x = 58, y = 18, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A2' AND room_number = '201' AND is_deleted = 0;
UPDATE room_table SET x = 58, y = 20, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A2' AND room_number = '301' AND is_deleted = 0;
"""

SQL_ROLLBACK = "SELECT 1;"


class Migration(migrations.Migration):

    dependencies = [
        ("team_USL", "0014_update_building_floor_range_B_to_G"),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_MIGRATE,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]
