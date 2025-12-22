# Generated manually - Change Member model fields

from django.db import migrations, models


def migrate_member_names(apps, schema_editor):
    """既存のfirst_name/last_nameをnameに統合"""
    db_alias = schema_editor.connection.alias

    # テーブルのカラムを確認
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(team_tansaibou_member)")
        columns = {row[1] for row in cursor.fetchall()}

    # last_name/first_name が存在する場合のみ移行
    if 'last_name' in columns and 'first_name' in columns:
        with schema_editor.connection.cursor() as cursor:
            # name カラムがなければ追加
            if 'name' not in columns:
                cursor.execute("""
                    ALTER TABLE team_tansaibou_member
                    ADD COLUMN name VARCHAR(100) DEFAULT ''
                """)
            # 既存データを移行（姓 + 名 → 名前）
            cursor.execute("""
                UPDATE team_tansaibou_member
                SET name = last_name || ' ' || first_name
                WHERE name = '' OR name IS NULL
            """)


def add_new_columns(apps, schema_editor):
    """新しいカラムを追加"""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(team_tansaibou_member)")
        columns = {row[1] for row in cursor.fetchall()}

    # student_id カラムがなければ追加
    if 'student_id' not in columns:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE team_tansaibou_member
                ADD COLUMN student_id VARCHAR(50) DEFAULT ''
            """)

    # email カラムがなければ追加
    if 'email' not in columns:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE team_tansaibou_member
                ADD COLUMN email VARCHAR(254) DEFAULT ''
            """)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('team_tansaibou', '0005_store_custom_auth'),
    ]

    operations = [
        # DB操作: 既存データを移行し、新カラムを追加
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Stateの変更: Memberモデルのフィールドを更新
                migrations.RemoveField(
                    model_name='member',
                    name='first_name',
                ),
                migrations.RemoveField(
                    model_name='member',
                    name='last_name',
                ),
                migrations.AddField(
                    model_name='member',
                    name='name',
                    field=models.CharField(max_length=100, verbose_name='名前'),
                ),
                migrations.AddField(
                    model_name='member',
                    name='student_id',
                    field=models.CharField(blank=True, max_length=50, verbose_name='学籍番号'),
                ),
                migrations.AddField(
                    model_name='member',
                    name='email',
                    field=models.EmailField(blank=True, max_length=254, verbose_name='メールアドレス'),
                ),
            ],
            database_operations=[
                migrations.RunPython(migrate_member_names, reverse_noop),
                migrations.RunPython(add_new_columns, reverse_noop),
            ],
        ),
    ]
