from django.db import migrations

SQL_SEED = """
INSERT OR IGNORE INTO floor_table (url, created_dt, updated_dt, floor) VALUES
  ('image/B-1.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B-1'),
  ('image/B-1.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B1-1'),
  ('image/B-1.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B2-1'),
  ('image/B-1.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B3-1'),
  ('image/B-2.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B-2'),
  ('image/B-2.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B1-2'),
  ('image/B-2.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B2-2'),
  ('image/B-2.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B3-2'),
  ('image/B-3.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B-3'),
  ('image/B-3.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B1-3'),
  ('image/B-3.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B2-3'),
  ('image/B-3.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B3-3'),
  ('image/B-4.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B-4'),
  ('image/B-4.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B1-4'),
  ('image/B-4.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B2-4'),
  ('image/B-4.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B3-4'),
  ('image/B-5.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B-5'),
  ('image/B-5.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B1-5'),
  ('image/B-5.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B2-5'),
  ('image/B-5.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'B3-5');
"""

SQL_ROLLBACK = """
DELETE FROM floor_table WHERE floor IN (
  'B-1', 'B1-1', 'B2-1', 'B3-1',
  'B-2', 'B1-2', 'B2-2', 'B3-2',
  'B-3', 'B1-3', 'B2-3', 'B3-3',
  'B-4', 'B1-4', 'B2-4', 'B3-4',
  'B-5', 'B1-5', 'B2-5', 'B3-5'
);
"""


class Migration(migrations.Migration):

    dependencies = [
        ("team_USL", "0011_insert_data_B"),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_SEED,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]
