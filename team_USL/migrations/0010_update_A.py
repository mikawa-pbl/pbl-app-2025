from django.db import migrations

# Valid Rooms Lists
ROOMS_A = [
    '101', '105', '106', '108', '109', '110', '111', '114',
    '201', '202', '203', '205', '207', '208', '209',
    '301', '302', '303', '304', '306', '307', '308', '309', '311', '312'
]
ROOMS_A1 = ['101', '201', '301']
ROOMS_A2 = ['101', '201', '301']

def generate_sql():
    sql_statements = []

    # 1. DELETE invalid rooms
    # Building A
    valid_a = "', '".join(ROOMS_A)
    sql_statements.append(f"DELETE FROM room_table WHERE building_id = 'A' AND room_number NOT IN ('{valid_a}') AND is_deleted = 0;")
    
    # Building A1
    valid_a1 = "', '".join(ROOMS_A1)
    sql_statements.append(f"DELETE FROM room_table WHERE building_id = 'A1' AND room_number NOT IN ('{valid_a1}') AND is_deleted = 0;")
    
    # Building A2
    valid_a2 = "', '".join(ROOMS_A2)
    sql_statements.append(f"DELETE FROM room_table WHERE building_id = 'A2' AND room_number NOT IN ('{valid_a2}') AND is_deleted = 0;")

    # 2. INSERT missing rooms (x=0, y=0)
    # Helper to create INSERT statement
    def create_insert(building, rooms):
        stmts = []
        for r in rooms:
            # Check if exists, if not insert
            stmts.append(f"""
            INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
            SELECT '{r}', '{building}', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
            WHERE NOT EXISTS (
                SELECT 1 FROM room_table WHERE room_number='{r}' AND building_id='{building}' AND is_deleted=0
            );
            """)
        return stmts

    sql_statements.extend(create_insert('A', ROOMS_A))
    sql_statements.extend(create_insert('A1', ROOMS_A1))
    sql_statements.extend(create_insert('A2', ROOMS_A2))

    # 3. UPDATE coordinates to 0,0 for all valid rooms except A-101
    # We update x, y to 0.0 where building is A/A1/A2 AND NOT (A-101).
    # This covers both newly inserted (already 0) and existing ones (forcing to 0).
    sql_statements.append("""
    UPDATE room_table 
    SET x = 0.0, y = 0.0, updated_dt = CURRENT_TIMESTAMP
    WHERE building_id IN ('A', 'A1', 'A2') 
      AND NOT (building_id = 'A' AND room_number = '101')
      AND is_deleted = 0;
    """)

    return "\n".join(sql_statements)

SQL_MIGRATE = generate_sql()

# For rollback, we might not be able to perfectly restore deleted data without a backup, 
# but we can try to reverse logical steps if needed. 
# For now, minimal rollback (just no-op or partial reverse) is acceptable given request context.
# We will define a dummy rollback or simple reverse for "inserted" data if feasible, 
# but deleting restored data is complex. We'll leave rollback empty or basic.
SQL_ROLLBACK = "SELECT 1;" 

class Migration(migrations.Migration):

    dependencies = [
        ('team_USL', '0009_auto_20260119_0632'),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_MIGRATE,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]
