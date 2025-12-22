# Generated manually - Store model with custom authentication
# No dependency on Django auth - fully self-contained in team_tansaibou DB
# Handles both fresh installs and migrations from old schema
# Database-agnostic: works with SQLite, PostgreSQL, MySQL

from django.db import migrations, models, connection
import django.db.models.deletion


def get_table_columns(cursor, table_name):
    """DB非依存でテーブルのカラム名一覧を取得"""
    columns = {col.name for col in connection.introspection.get_table_description(cursor, table_name)}
    return columns


def table_exists(cursor, table_name):
    """DB非依存でテーブルの存在確認"""
    return table_name in connection.introspection.table_names(cursor)


def create_or_update_store_table(apps, schema_editor):
    """Storeテーブルを作成、または既存テーブルに新カラムを追加"""
    with schema_editor.connection.cursor() as cursor:
        if not table_exists(cursor, 'team_tansaibou_store'):
            # テーブルが存在しない場合は作成
            cursor.execute("""
                CREATE TABLE team_tansaibou_store (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) NOT NULL DEFAULT '',
                    password VARCHAR(128) NOT NULL DEFAULT '',
                    name VARCHAR(100) NOT NULL,
                    slug VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT NOT NULL DEFAULT '',
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            return

        # 既存テーブルのカラムを確認
        columns = get_table_columns(cursor, 'team_tansaibou_store')

        # usernameカラムがなければ追加
        if 'username' not in columns:
            cursor.execute("""
                ALTER TABLE team_tansaibou_store
                ADD COLUMN username VARCHAR(50) DEFAULT ''
            """)

        # passwordカラムがなければ追加
        if 'password' not in columns:
            cursor.execute("""
                ALTER TABLE team_tansaibou_store
                ADD COLUMN password VARCHAR(128) DEFAULT ''
            """)

        # is_activeカラムがなければ追加
        if 'is_active' not in columns:
            cursor.execute("""
                ALTER TABLE team_tansaibou_store
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE
            """)


def add_store_field_to_table(apps, schema_editor, table_name):
    """既存テーブルにstore_idカラムを追加（存在しない場合のみ）"""
    with schema_editor.connection.cursor() as cursor:
        columns = get_table_columns(cursor, table_name)

        if 'store_id' not in columns:
            cursor.execute(f"""
                ALTER TABLE {table_name}
                ADD COLUMN store_id bigint NULL REFERENCES team_tansaibou_store(id)
            """)


def add_store_fields(apps, schema_editor):
    """各テーブルにstore_idを追加"""
    tables = [
        'team_tansaibou_member',
        'team_tansaibou_product',
        'team_tansaibou_productset',
        'team_tansaibou_transaction',
    ]
    for table in tables:
        add_store_field_to_table(apps, schema_editor, table)


def migrate_existing_store_data(apps, schema_editor):
    """既存データにusername/passwordを設定"""
    from django.contrib.auth.hashers import make_password

    db_alias = schema_editor.connection.alias

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


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('team_tansaibou', '0004_productset_productsetitem_delete_dailysummary_and_more'),
    ]

    operations = [
        # DB操作とState操作を分離
        # State: DjangoにStoreモデルを認識させる
        # DB: テーブルが存在しなければ作成、存在すればカラム追加
        migrations.SeparateDatabaseAndState(
            state_operations=[
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
            ],
            database_operations=[
                migrations.RunPython(create_or_update_store_table, reverse_noop),
            ],
        ),
        # 各モデルにstoreフィールドを追加
        migrations.SeparateDatabaseAndState(
            state_operations=[
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
            ],
            database_operations=[
                migrations.RunPython(add_store_fields, reverse_noop),
            ],
        ),
        # 既存データにusername/passwordを設定
        migrations.RunPython(migrate_existing_store_data, reverse_noop),
    ]
