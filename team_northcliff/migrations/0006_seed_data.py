from django.db import migrations
from django.utils import timezone
import random


def seed_data(apps, schema_editor):
    Facility = apps.get_model("team_northcliff", "Facility")
    User = apps.get_model("team_northcliff", "User")
    Post = apps.get_model("team_northcliff", "Post")
    FacilityAccess = apps.get_model("team_northcliff", "FacilityAccess")

    # Seed Facilities
    facilities_data = [
        {"facility_id": "lib", "name": "🏢 図書館"},
        {"facility_id": "hiba", "name": "🍴 食堂（ひばり）"},
        {"facility_id": "kita", "name": "🅿️ 北駐車場"},
        #{"facility_id": "cafe", "name": "☕️ カフェ"},
        {"facility_id": "bus", "name": "🚌 バス停"},
        {"facility_id": "gym", "name": "🏋️ ジム"},
    ]
    facilities = []
    for data in facilities_data:
        facility, _ = Facility.objects.get_or_create(**data)
        facilities.append(facility)

    # Seed Users
    user_names = ["田中太郎", "鈴木花子", "佐藤次郎", "高橋美咲", "伊藤健太"]
    users = []
    for name in user_names:
        user, _ = User.objects.get_or_create(
            name=name, defaults={"points": random.randint(10, 100)}
        )
        users.append(user)

    # Seed Posts
    statuses = ["empty", "moderate", "crowded"]
    comments_list = [
        "とても静かです",
        " 混雑していますね",
        "快適な環境です",
        "もう一杯です",
        "人が少ないですよ",
        "おすすめです",
        "混雑中です",
        "空いていますね",
        None,
        None,
    ]

    for i in range(10):
        Post.objects.get_or_create(
            user=random.choice(users),
            facility=random.choice(facilities),
            defaults={
                "status": random.choice(statuses),
                "comment": random.choice(comments_list),
                "created_at": timezone.now()
                - timezone.timedelta(hours=random.randint(0, 24)),
            },
        )

    # Seed FacilityAccess
    for user in users:
        for facility in random.sample(facilities, k=random.randint(2, 4)):
            FacilityAccess.objects.get_or_create(
                user=user,
                facility=facility,
            )


def reverse_seed(apps, schema_editor):
    Facility = apps.get_model("team_northcliff", "Facility")
    User = apps.get_model("team_northcliff", "User")
    Post = apps.get_model("team_northcliff", "Post")
    FacilityAccess = apps.get_model("team_northcliff", "FacilityAccess")

    Facility.objects.all().delete()
    User.objects.all().delete()
    Post.objects.all().delete()
    FacilityAccess.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("team_northcliff", "0005_facility_user_post_facilityaccess"),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
