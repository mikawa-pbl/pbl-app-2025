from django.db import migrations

SQL_SEED = """
INSERT OR IGNORE INTO building_floor_range (building_name, min_floor, max_floor) VALUES
  ('A',  1, 3),
  ('A-1', 1, 3),
  ('A-2', 1, 3),
  ('B',  1, 3), -- 仮のデータ
  ('C',  1, 6);
"""

SQL_ROLLBACK = """
DELETE FROM building_floor_range WHERE building_name IN ('A', 'A-1', 'A-2', 'B', 'C');
"""

class Migration(migrations.Migration):

    dependencies = [
        ('team_USL', '0007_buildingfloorrange'),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_SEED,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]