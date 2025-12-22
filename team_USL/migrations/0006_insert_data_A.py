from django.db import migrations

SQL_SEED = """
-- floor_table: 手動で追加したフロア情報を投入（重複時は無視）
INSERT OR IGNORE INTO floor_table (url, created_dt, updated_dt, floor) VALUES
  ('images/A-1.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A1-1'),
  ('images/A-2.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A1-2'),
  ('images/A-3.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A1-3'),
  ('images/A-1.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A2-1'),
  ('images/A-2.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A2-2'),
  ('images/A-3.png', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'A2-3');

-- room_table: 既存seed(0005)の101座標を上書き（※building_id='A'のみ）
UPDATE room_table
SET x = 82.0, y = 90.0, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '101' AND is_deleted = 0;

-- room_table: 手動で追加した部屋情報を投入（同一キーが既にあれば追加しない）
INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '105', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='105' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '106', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='106' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '108', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='108' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '109', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='109' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '110', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='110' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '111', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='111' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '114', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='114' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '115', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='115' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '116', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='116' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '117', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='117' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '118', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='118' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '119', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='119' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '120', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='120' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '121', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='121' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '122', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='122' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '123', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='123' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '201', 'A1', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='201' AND building_id='A1' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '301', 'A1', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='301' AND building_id='A1' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '101', 'A1', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='101' AND building_id='A1' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '201', 'A2', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='201' AND building_id='A2' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '301', 'A2', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='301' AND building_id='A2' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '101', 'A2', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='101' AND building_id='A2' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '201', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='201' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '301', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='301' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '302', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='302' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '303', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='303' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '304', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='304' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '305', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='305' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '306', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='306' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '307', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='307' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '308', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='308' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '309', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='309' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '311', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='311' AND building_id='A' AND is_deleted=0
);

INSERT INTO room_table (room_number, building_id, x, y, created_dt, updated_dt, is_deleted)
SELECT '312', 'A', 0.0, 0.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0
WHERE NOT EXISTS (
  SELECT 1 FROM room_table
  WHERE room_number='312' AND building_id='A' AND is_deleted=0
);
"""

SQL_ROLLBACK = """
-- room_table: このmigrationで投入した部屋情報を削除
DELETE FROM room_table WHERE room_number='105' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='106' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='108' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='109' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='110' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='111' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='114' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='115' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='116' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='117' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='118' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='119' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='120' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='121' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='122' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='123' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='201' AND building_id='A1' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='301' AND building_id='A1' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='101' AND building_id='A1' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='201' AND building_id='A2' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='301' AND building_id='A2' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='101' AND building_id='A2' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='201' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='301' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='302' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='303' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='304' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='305' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='306' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='307' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='308' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='309' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='311' AND building_id='A' AND is_deleted=0;
DELETE FROM room_table WHERE room_number='312' AND building_id='A' AND is_deleted=0;

-- room_table: 101座標の上書きを元に戻す（0005 seed相当）
UPDATE room_table
SET x = 0.0, y = 0.0, updated_dt = CURRENT_TIMESTAMP
WHERE building_id = 'A' AND room_number = '101' AND is_deleted = 0;

-- floor_table: このmigrationで投入したフロア情報を削除
DELETE FROM floor_table WHERE floor IN ('A1-1', 'A1-2', 'A1-3', 'A2-1', 'A2-2', 'A2-3');
"""

class Migration(migrations.Migration):

    dependencies = [
        ('team_USL', '0005_insert_data'),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL_SEED,
            reverse_sql=SQL_ROLLBACK,
        ),
    ]
