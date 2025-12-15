from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("h34vvy_u53rzz", "0003_entry_door_comment_entry_door_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="entry",
            name="body",
        ),
        migrations.RenameField(
            model_name="entry",
            old_name="door_comment",
            new_name="comment",
        ),
    ]
