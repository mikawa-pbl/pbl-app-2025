from django.db import migrations

SQL_MIGRATE = """
UPDATE floor_table
SET url = REPLACE(url, 'image/', 'images/')
WHERE url LIKE 'image/%';
"""

SQL_ROLLBACK = """
UPDATE floor_table
SET url = REPLACE(url, 'images/', 'image/')
WHERE url LIKE 'images/%';
"""


class Migration(migrations.Migration):

    dependencies = [
        ("team_USL", "0012_insert_data_B_floor"),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_MIGRATE,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]
