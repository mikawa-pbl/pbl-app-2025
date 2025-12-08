# Generated manually - Store model with custom authentication
# No dependency on Django auth - fully self-contained in team_tansaibou DB

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team_tansaibou', '0004_productset_productsetitem_delete_dailysummary_and_more'),
    ]

    operations = [
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
