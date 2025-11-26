# team_TeXTeX/management/commands/seed_and_reset.py (シンプル版)

from django.core.management.base import BaseCommand
from django.db import transaction
from team_TeXTeX.models import Group, Content 
from team_TeXTeX.data import SEED_DATA 


class Command(BaseCommand):
    help = 'GroupとContentの全データを削除し、data.pyのデータで新規作成します。'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- データリセット＆再投入開始 ---"))

        with transaction.atomic():
            
            # ---------------------------
            # 1. 既存データの全削除 (リセット)
            # ---------------------------
            self.stdout.write(self.style.WARNING("🗑️ 既存のGroupとContentのデータを全て削除します..."))
            deleted_count, _ = Group.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"✅ Groupおよび関連Content {deleted_count} 件の削除が完了しました。"))

            # ---------------------------
            # 2. data.pyに基づいた新規データの作成（再投入）
            # ---------------------------
            for group_data in SEED_DATA:
                
                group_instance = Group.objects.create(title=group_data.title)
                self.stdout.write(f"✅ Group '{group_instance.title}' を新規作成しました。 (ID: {group_instance.id})")

                # Contentレコードの作成
                for content_data in group_data.contents:
                    content_instance = Content.objects.create(
                        group=group_instance,
                        name=content_data.name,
                        function_slug=content_data.function_slug,
                        tex_code=content_data.tex_code,
                        guide_content=content_data.guide_content,
                    )
                self.stdout.write(f"   ∟ Content {len(group_data.contents)}件を関連付けました。")

        self.stdout.write(self.style.SUCCESS("\n🎉 リセットとデータの再投入が全て完了しました！"))
        