from django.db import migrations

SQL_MIGRATE = """
UPDATE building_floor_range
SET max_floor = 5
WHERE building_name = 'B';

UPDATE building_floor_range
SET max_floor = 5
WHERE building_name = 'C';

INSERT OR IGNORE INTO building_floor_range (building_name, min_floor, max_floor) VALUES
  ('D', 1, 8),
  ('F', 1, 5),
  ('G', 1, 6);
"""

SQL_ROLLBACK = """
UPDATE building_floor_range
SET max_floor = 3
WHERE building_name = 'B';

UPDATE building_floor_range
SET max_floor = 6
WHERE building_name = 'C';

DELETE FROM building_floor_range WHERE building_name IN ('D', 'F', 'G');
"""


class Migration(migrations.Migration):

    dependencies = [
        ("team_USL", "0013_update_floor_image_paths"),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_MIGRATE,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]
