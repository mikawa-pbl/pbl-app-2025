from django.db import migrations

SQL_SEED = """
INSERT INTO team_northcliff_member -- TODO: app名_memberに変更
(first_name, last_name)
VALUES
  ('Ryo', 'Saito'),
  ('Kazuma', 'Oda'),
  ('Yuya', 'Kumagai'),
  ('Outdam', 'Ouk');
"""

SQL_ROLLBACK = """
DELETE FROM team_northcliff_member -- TODO: app名_memberに変更
WHERE (first_name='Ryo' AND last_name='Saito')
   OR (first_name='Kazuma' AND last_name='Oda')
   OR (first_name='Yuya' AND last_name='Kumagai')
   OR (first_name='Outdam' AND last_name='Ouk');
"""

class Migration(migrations.Migration):
    dependencies = [
        ('team_northcliff', '0001_initial'),  # TODO: app名に変更
    ]
    operations = [
        migrations.RunSQL(
            sql=SQL_SEED,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]