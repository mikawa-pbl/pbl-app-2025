# 初期教室データの投入

from django.db import migrations


def add_initial_data(apps, schema_editor):
    Building = apps.get_model('agileca', 'Building')
    Professor = apps.get_model('agileca', 'Professor')
    Attribute = apps.get_model('agileca', 'Attribute')
    Classroom = apps.get_model('agileca', 'Classroom')
    ClassroomAttribute = apps.get_model('agileca', 'ClassroomAttribute')

    # ---------- Building ----------
    b1 = Building.objects.create(name="A")
    b2 = Building.objects.create(name="図書館")
    b3 = Building.objects.create(name="IMC")
    b4 = Building.objects.create(name="B")
    b5 = Building.objects.create(name="F")

    # ---------- Professor ----------
    p1 = Professor.objects.create(name="鈴木")
    p2 = Professor.objects.create(name="後藤")
    p3 = Professor.objects.create(name="Dall'Arno")

    # ---------- Attribute ----------
    a1 = Attribute.objects.create(name="自習")
    a2 = Attribute.objects.create(name="飲食")
    a3 = Attribute.objects.create(name="奨学金")
    a4 = Attribute.objects.create(name="運動")

    # ---------- Classroom ----------
    # professor は None を設定すると SQL の NULL として保存される

    c1 = Classroom.objects.create(building=b1, room_name="A-101",   floor="1", professor=None)
    c2 = Classroom.objects.create(building=b2, room_name="図書館1階", floor="1", professor=None)
    c3 = Classroom.objects.create(building=b3, room_name="IMC1階",  floor="1", professor=None)
    c4 = Classroom.objects.create(building=b4, room_name="教務課",   floor="1", professor=None)
    c5 = Classroom.objects.create(building=b5, room_name="F-503",   floor="5", professor=p1)

    # ---------- ClassroomAttribute（中間テーブル） ----------
    ClassroomAttribute.objects.create(classroom=c1, attribute=a1)
    ClassroomAttribute.objects.create(classroom=c1, attribute=a2)

    ClassroomAttribute.objects.create(classroom=c2, attribute=a1)
    ClassroomAttribute.objects.create(classroom=c2, attribute=a2)

    ClassroomAttribute.objects.create(classroom=c3, attribute=a3)
    ClassroomAttribute.objects.create(classroom=c4, attribute=a4)


def remove_initial_data(apps, schema_editor):
    Building = apps.get_model('agileca', 'Building')
    Professor = apps.get_model('agileca', 'Professor')
    Attribute = apps.get_model('agileca', 'Attribute')
    Classroom = apps.get_model('agileca', 'Classroom')
    ClassroomAttribute = apps.get_model('agileca', 'ClassroomAttribute')

    # 中間テーブル削除
    ClassroomAttribute.objects.all().delete()

    # 教室削除
    Classroom.objects.all().delete()

    # 属性削除
    Attribute.objects.all().delete()

    # 教授削除（鈴木先生のみ）
    Professor.objects.all().delete()

    # 建物削除
    Building.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('agileca', '0002_attribute_building_classroom_professor_and_more'),
    ]

    operations = [
        migrations.RunPython(add_initial_data, remove_initial_data),
    ]
