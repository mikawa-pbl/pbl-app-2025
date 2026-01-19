# Generated manually to load companies from CSV

import csv
import os
from django.db import migrations


def load_companies(apps, schema_editor):
    Company = apps.get_model('team_UD', 'Company')
    
    # CSVファイルのパス
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'fixtures',
        'companies.csv'
    )
    
    # CSVファイルを読み込んで会社を登録
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        companies = []
        for row in reader:
            company_name = row['name'].strip()
            if company_name:  # 空行をスキップ
                companies.append(Company(name=company_name))
        
        # バルクインサートで一括登録
        Company.objects.bulk_create(companies, ignore_conflicts=True)
        print(f"登録された会社数: {len(companies)}")


def remove_companies(apps, schema_editor):
    Company = apps.get_model('team_UD', 'Company')
    Company.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('team_UD', '0006_company_remove_memo_company_name_memo_company'),
    ]

    operations = [
        migrations.RunPython(load_companies, remove_companies),
    ]
