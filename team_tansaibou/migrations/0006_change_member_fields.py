# Generated manually - Change Member model fields
# Database-agnostic: works with SQLite, PostgreSQL, MySQL

from django.db import migrations, models, connection


def get_table_columns(cursor, table_name):
    """DB非依存でテーブルのカラム名一覧を取得"""
    return {col.name for col in connection.introspection.get_table_description(cursor, table_name)}


def migrate_member_names(apps, schema_editor):
    """既存のfirst_name/last_nameをnameに統合"""
    with schema_editor.connection.cursor() as cursor:
        columns = get_table_columns(cursor, 'team_tansaibou_member')

        # last_name/first_name が存在する場合のみ移行
        if 'last_name' in columns and 'first_name' in columns:
            # name カラムがなければ追加
            if 'name' not in columns:
                cursor.execute("""
                    ALTER TABLE team_tansaibou_member
                    ADD COLUMN name VARCHAR(100) DEFAULT ''
                """)
            # 既存データを移行（姓 + 名 → 名前）
            # PostgreSQL/MySQL/SQLiteで動作する文字列連結
            cursor.execute("""
                UPDATE team_tansaibou_member
                SET name = last_name || ' ' || first_name
                WHERE name = '' OR name IS NULL
            """)


def add_new_columns(apps, schema_editor):
    """新しいカラムを追加"""
    with schema_editor.connection.cursor() as cursor:
        columns = get_table_columns(cursor, 'team_tansaibou_member')

        # student_id カラムがなければ追加
        if 'student_id' not in columns:
            cursor.execute("""
                ALTER TABLE team_tansaibou_member
                ADD COLUMN student_id VARCHAR(50) DEFAULT ''
            """)

        # email カラムがなければ追加
        if 'email' not in columns:
            cursor.execute("""
                ALTER TABLE team_tansaibou_member
                ADD COLUMN email VARCHAR(254) DEFAULT ''
            """)


def remove_old_columns(apps, schema_editor):
    """古いfirst_name/last_nameカラムを削除（SQLite対応）"""
    with schema_editor.connection.cursor() as cursor:
        columns = get_table_columns(cursor, 'team_tansaibou_member')

        # 古いカラムがなければスキップ
        if 'first_name' not in columns and 'last_name' not in columns:
            return

        # SQLiteではALTER TABLE DROP COLUMNが使えない場合があるため
        # テーブルを再作成する
        cursor.execute("""
            CREATE TABLE team_tansaibou_member_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL DEFAULT '',
                student_id VARCHAR(50) NOT NULL DEFAULT '',
                email VARCHAR(254) NOT NULL DEFAULT '',
                store_id BIGINT NULL REFERENCES team_tansaibou_store(id)
            )
        """)

        # データを移行
        cursor.execute("""
            INSERT INTO team_tansaibou_member_new (id, name, student_id, email, store_id)
            SELECT id, name, student_id, email, store_id
            FROM team_tansaibou_member
        """)

        # 古いテーブルを削除して新しいテーブルをリネーム
        cursor.execute("DROP TABLE team_tansaibou_member")
        cursor.execute("ALTER TABLE team_tansaibou_member_new RENAME TO team_tansaibou_member")


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
                migrations.RunPython(remove_old_columns, reverse_noop),
            ],
        ),
    ]
