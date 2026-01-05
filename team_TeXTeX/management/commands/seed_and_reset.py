from django.core.management.base import BaseCommand
from django.db import connection, transaction
from team_TeXTeX.models import Groups, Contents, Slugs, Guides, Users, Favorites
from team_TeXTeX.data import SEED_DATA

class Command(BaseCommand):
    help = 'Drops legacy tables, resets new tables, and seeds data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Starting DB Cleanup and Seeding ---"))

        # 1. Drop Legacy Tables (Raw SQL)
        # These are the tables from the old schema (Group, Content)
        legacy_tables = ['team_TeXTeX_group', 'team_TeXTeX_content']
        with connection.cursor() as cursor:
            for table in legacy_tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                self.stdout.write(f"Dropped legacy table (if existed): {table}")

        # 2. Reset and Seed New Tables (Django ORM)
        with transaction.atomic():
            self.stdout.write("Clearing existing data from new tables...")
            Contents.objects.all().delete()
            Groups.objects.all().delete()
            Slugs.objects.all().delete()
            Guides.objects.all().delete()
            Users.objects.all().delete() # Usersもクリア
            Favorites.objects.all().delete() # Favoritesもクリア

            # Create User "Alice"
            Users.objects.create(user_id=1, user="Alice")
            self.stdout.write("Created User: Alice (ID: 1)")

            self.stdout.write("Seeding new data...")
            for group_data in SEED_DATA:
                # Create Group
                group_instance = Groups.objects.create(
                    title=group_data.title,
                    group_id=group_data.group_id
                )
                self.stdout.write(f"Created Group: {group_instance.title} (ID: {group_instance.group_id})")

                for content_data in group_data.contents:
                    # Create Slug
                    slug_instance = Slugs.objects.create(
                        function_slug=content_data.function_slug,
                        slug_id=content_data.slug_id
                    )

                    # Create Guide
                    guide_instance = Guides.objects.create(
                        guide_content=content_data.guide_content,
                        guide_id=content_data.guide_id
                    )

                    # Create Content
                    Contents.objects.create(
                        group=group_instance,
                        slug=slug_instance,
                        guide=guide_instance,
                        name=content_data.name,
                        tex_code=content_data.tex_code,
                    )
                self.stdout.write(f"  Added {len(group_data.contents)} contents to group.")

        self.stdout.write(self.style.SUCCESS("--- Cleanup and Seeding Complete! ---"))
