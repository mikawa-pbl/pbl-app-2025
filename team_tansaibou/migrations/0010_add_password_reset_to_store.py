from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_tansaibou', '0009_add_cost_price_to_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='メールアドレス'),
        ),
        migrations.AddField(
            model_name='store',
            name='password_reset_token',
            field=models.CharField(blank=True, max_length=100, verbose_name='パスワードリセットトークン'),
        ),
        migrations.AddField(
            model_name='store',
            name='password_reset_expires',
            field=models.DateTimeField(blank=True, null=True, verbose_name='トークン有効期限'),
        ),
    ]
