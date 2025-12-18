# Generated migration for initial data

from django.db import migrations

def create_initial_data(apps, schema_editor):
    Tag = apps.get_model('takenoko', 'Tag')
    TargetGrade = apps.get_model('takenoko', 'TargetGrade')
    
    # タグを登録
    tags_data = [
        {'name': 'textbook', 'display_name': '書籍'},
        {'name': 'reference', 'display_name': '日用品'},
        {'name': 'notes', 'display_name': '家具'},
        {'name': 'stationery', 'display_name': '電子機器'},
        {'name': 'electronics', 'display_name': '服飾品'},
        {'name': 'furniture', 'display_name': '乗り物'},
        {'name': 'clothing', 'display_name': '過去問'},
        {'name': 'other', 'display_name': 'その他'},
    ]
    
    for tag_data in tags_data:
        Tag.objects.get_or_create(**tag_data)
    
    # 対象学年を登録
    grades_data = [
        {'code': 'b1', 'display_name': '学部1年向け'},
        {'code': 'b2', 'display_name': '学部2年向け'},
        {'code': 'b3', 'display_name': '学部3年向け'},
        {'code': 'b4', 'display_name': '学部4年向け'},
        {'code': 'm1', 'display_name': '修士1年向け'},
        {'code': 'm2', 'display_name': '修士2年向け'},
        {'code': 'd', 'display_name': '博士課程向け'},
        {'code': 'all', 'display_name': '全学年向け'},
    ]
    
    for grade_data in grades_data:
        TargetGrade.objects.get_or_create(**grade_data)

def reverse_initial_data(apps, schema_editor):
    Tag = apps.get_model('takenoko', 'Tag')
    TargetGrade = apps.get_model('takenoko', 'TargetGrade')
    Tag.objects.all().delete()
    TargetGrade.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('takenoko', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, reverse_initial_data),
    ]