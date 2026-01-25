from django.db import migrations

ROOM_LIST = [
    "B-104",
    "B-108",
    "B1-101",
    "B1-103",
    "B1-104",
    "B2-101",
    "B2-102",
    "B2-103",
    "B2-104",
    "B2-105",
    "B2-106",
    "B2-107",
    "B2-108",
    "B2-109",
    "B2-110",
    "B2-111",
    "B-201",
    "B-202",
    "B-203",
    "B-204",
    "B-205",
    "B-206",
    "B-207",
    "B-209",
    "B-210",
    "B-211",
    "B-212",
    "B1-201",
    "B1-202",
    "B1-203",
    "B2-201",
    "B2-202",
    "B2-203",
    "B2-204",
    "B2-205",
    "B2-206",
    "B2-207",
    "B2-208",
    "B2-209",
    "B2-210",
    "B3-201",
    "B-301",
    "B-302",
    "B-303",
    "B-304",
    "B-305",
    "B-306",
    "B-307",
    "B-308",
    "B-309",
    "B-310",
    "B-311",
    "B-312",
    "B-313",
    "B-315",
    "B-316",
    "B-317",
    "B-318",
    "B-319",
    "B-320",
    "B-321",
    "B1-301",
    "B1-302",
    "B1-305",
    "B2-301",
    "B2-302",
    "B2-303",
    "B2-304",
    "B2-305",
    "B2-306",
    "B2-307",
    "B2-308",
    "B2-209",
    "B3-301",
    "B-401",
    "B-402",
    "B-403",
    "B-404",
    "B-405",
    "B-406",
    "B-407",
    "B-408",
    "B-409",
    "B-410",
    "B-411",
    "B-412",
    "B-413",
    "B-414",
    "B-415",
    "B-416",
    "B-417",
    "B-418",
    "B2-401",
    "B2-402",
    "B2-403",
    "B2-404",
    "B2-405",
    "B2-406",
    "B2-407",
    "B2-408",
    "B2-409",
    "B-501",
    "B-502",
    "B-503",
    "B-504",
    "B-505",
    "B-506",
    "B-507",
    "B-508",
    "B-509",
    "B-510",
    "B-511",
    "B-512",
    "B-513",
    "B-514",
    "B-515",
    "B-516-1",
    "B-516-2",
    "B-517",
    "B-518",
    "B-519",
    "B-520",
    "B2-501",
    "B2-502",
    "B2-503",
    "B2-504",
    "B2-505",
    "B2-506",
    "B2-507",
    "B2-508",
    "B2-509",
]


def build_sql():
    statements = []
    for entry in ROOM_LIST:
        building_id, room_number = entry.split("-", 1)
        statements.append(
            f"""
            INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
            SELECT '{room_number}', '{building_id}', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
            WHERE NOT EXISTS (
                SELECT 1 FROM room_table
                WHERE room_number='{room_number}' AND building_id='{building_id}' AND is_deleted=0
            );
            """
        )
    return "\n".join(statements)


SQL_MIGRATE = build_sql()
SQL_ROLLBACK = "SELECT 1;"


class Migration(migrations.Migration):

    dependencies = [
        ("team_USL", "0010_update_A"),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_MIGRATE,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]
