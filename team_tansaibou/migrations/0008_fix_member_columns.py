# Generated manually - Fix Member table columns
# Removes old first_name/last_name columns and ensures new columns exist

from django.db import migrations


def fix_member_table(apps, schema_editor):
    """本番DBのMemberテーブルを修正"""
    with schema_editor.connection.cursor() as cursor:
        # SQLiteのPRAGMAで現在のカラムを確認
        cursor.execute("PRAGMA table_info(team_tansaibou_member)")
        columns = {row[1] for row in cursor.fetchall()}

        # nameカラムがなければ追加
        if 'name' not in columns:
            cursor.execute("""
                ALTER TABLE team_tansaibou_member
                ADD COLUMN name VARCHAR(100) DEFAULT ''
            """)
            # first_name + last_name からデータ移行
            if 'first_name' in columns and 'last_name' in columns:
                cursor.execute("""
                    UPDATE team_tansaibou_member
                    SET name = last_name || ' ' || first_name
                """)

        # student_idカラムがなければ追加
        if 'student_id' not in columns:
            cursor.execute("""
                ALTER TABLE team_tansaibou_member
                ADD COLUMN student_id VARCHAR(50) DEFAULT ''
            """)

        # emailカラムがなければ追加
        if 'email' not in columns:
            cursor.execute("""
                ALTER TABLE team_tansaibou_member
                ADD COLUMN email VARCHAR(254) DEFAULT ''
            """)

        # first_name/last_nameがあればテーブル再作成して削除
        if 'first_name' in columns or 'last_name' in columns:
            cursor.execute("""
                CREATE TABLE team_tansaibou_member_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL DEFAULT '',
                    student_id VARCHAR(50) NOT NULL DEFAULT '',
                    email VARCHAR(254) NOT NULL DEFAULT '',
                    store_id BIGINT NULL
                )
            """)
            cursor.execute("""
                INSERT INTO team_tansaibou_member_new (id, name, student_id, email, store_id)
                SELECT id,
                       COALESCE(name, ''),
                       COALESCE(student_id, ''),
                       COALESCE(email, ''),
                       store_id
                FROM team_tansaibou_member
            """)
            cursor.execute("DROP TABLE team_tansaibou_member")
            cursor.execute("ALTER TABLE team_tansaibou_member_new RENAME TO team_tansaibou_member")


class Migration(migrations.Migration):

    dependencies = [
        ('team_tansaibou', '0007_alter_member_options'),
    ]

    operations = [
        migrations.RunPython(fix_member_table, migrations.RunPython.noop),
    ]
