from __future__ import annotations

from django.core.management.base import BaseCommand

from routers import TeamPerAppRouter


class Command(BaseCommand):
    help = "チーム/アプリごとのGroup（group名 == app_label）を不足分だけ作成します。"

    def handle(self, *args, **options):
        from django.contrib.auth.models import Group

        created = 0
        for app_label in sorted(TeamPerAppRouter.app_to_db.keys()):
            _, was_created = Group.objects.get_or_create(name=app_label)
            created += int(was_created)

        if created:
            self.stdout.write(self.style.SUCCESS(f"{created}件のGroupを作成しました。"))
        else:
            self.stdout.write("変更なし（全てのGroupが既に存在します）。")
