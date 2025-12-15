from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("h34vvy_u53rzz", "0004_entry_remove_body_rename_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="entry",
            name="helper_confirmed_at",
            field=models.DateTimeField(
                blank=True,
                help_text="ヘルパーが応答した日時",
                null=True,
            ),
        ),
    ]
