# Generated manually to convert Store.user (OneToOneField) to user_id (IntegerField)
# This avoids cross-database FK issues between team_tansaibou and default databases

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_tansaibou', '0005_store_member_store_product_store_productset_store_and_more'),
    ]

    operations = [
        # Step 1: Add the new user_id field (nullable temporarily)
        migrations.AddField(
            model_name='store',
            name='user_id_new',
            field=models.IntegerField(verbose_name='ユーザーID', null=True),
        ),
        # Step 2: Copy data from user_id (from FK) to user_id_new
        migrations.RunSQL(
            sql="UPDATE team_tansaibou_store SET user_id_new = user_id;",
            reverse_sql="UPDATE team_tansaibou_store SET user_id = user_id_new;",
        ),
        # Step 3: Remove the old user FK field
        migrations.RemoveField(
            model_name='store',
            name='user',
        ),
        # Step 4: Rename user_id_new to user_id
        migrations.RenameField(
            model_name='store',
            old_name='user_id_new',
            new_name='user_id',
        ),
        # Step 5: Make user_id non-nullable and unique
        migrations.AlterField(
            model_name='store',
            name='user_id',
            field=models.IntegerField(verbose_name='ユーザーID', unique=True),
        ),
    ]
