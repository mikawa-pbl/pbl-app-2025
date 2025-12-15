# Generated manually - Store model with custom authentication
# No dependency on Django auth - fully self-contained in team_tansaibou DB
# Handles both fresh installs and migrations from old schema

from django.db import migrations, models
import django.db.models.deletion


def check_and_migrate_store(apps, schema_editor):
    """既存のStoreテーブルがあれば、新しいカラムを追加してデータを移行"""
    from django.db import connection
    from django.contrib.auth.hashers import make_password

    db_alias = schema_editor.connection.alias

    # テーブルが存在するか確認
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='team_tansaibou_store'
        """)
        table_exists = cursor.fetchone() is not None

    if not table_exists:
        # テーブルが存在しない場合は何もしない（CreateModelで作成される）
        return

    # 既存テーブルのカラムを確認
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(team_tansaibou_store)")
        columns = {row[1] for row in cursor.fetchall()}

    # usernameカラムがなければ追加
    if 'username' not in columns:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE team_tansaibou_store
                ADD COLUMN username VARCHAR(50) DEFAULT ''
            """)

    # passwordカラムがなければ追加
    if 'password' not in columns:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE team_tansaibou_store
                ADD COLUMN password VARCHAR(128) DEFAULT ''
            """)

    # is_activeカラムがなければ追加
    if 'is_active' not in columns:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE team_tansaibou_store
                ADD COLUMN is_active BOOLEAN DEFAULT 1
            """)

    # 既存データにusername/passwordを設定
    Store = apps.get_model('team_tansaibou', 'Store')
    for store in Store.objects.using(db_alias).all():
        changed = False
        if not store.username:
            if hasattr(store, 'slug') and store.slug:
                store.username = store.slug
            else:
                store.username = f"store_{store.id}"
            changed = True
        if not store.password:
            store.password = make_password("password")
            changed = True
        if changed:
            store.save(using=db_alias)


def reverse_check(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('team_tansaibou', '0004_productset_productsetitem_delete_dailysummary_and_more'),
    ]

    operations = [
        # まずPythonでテーブルの状態を確認し、必要に応じてカラムを追加
        migrations.RunPython(check_and_migrate_store, reverse_check),

        # 新規インストールの場合のみCreateModelが効く
        # 既存テーブルがある場合は上のRunPythonで対応済み
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, unique=True, verbose_name='ログインID')),
                ('password', models.CharField(max_length=128, verbose_name='パスワード')),
                ('name', models.CharField(max_length=100, verbose_name='店舗名')),
                ('slug', models.SlugField(unique=True, verbose_name='識別子')),
                ('description', models.TextField(blank=True, verbose_name='説明')),
                ('is_active', models.BooleanField(default=True, verbose_name='有効')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
            options={
                'verbose_name': '店舗',
                'verbose_name_plural': '店舗',
            },
        ),
        migrations.AddField(
            model_name='member',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='team_tansaibou.store', verbose_name='店舗'),
        ),
        migrations.AddField(
            model_name='product',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='team_tansaibou.store', verbose_name='店舗'),
        ),
        migrations.AddField(
            model_name='productset',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_sets', to='team_tansaibou.store', verbose_name='店舗'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='team_tansaibou.store', verbose_name='店舗'),
        ),
    ]
