#!/usr/bin/env python
"""
科目データベース構築スクリプト

CSVディレクトリパスを引数に取り、科目情報をデータベースに登録する。
年度はディレクトリ名から取得する。

使用方法:
    python build_course_db.py <csv_directory_path>
    例: python build_course_db.py graphics/2025
"""

import os
import sys
import django
import csv
import re
from pathlib import Path

# Djangoプロジェクトのルートディレクトリを追加
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pbl_project.settings')
django.setup()

from graphics.models import Subject, Teacher, Department, CourseOffering


def parse_teachers(teacher_str):
    """
    担当教員の文字列をパースして教員名のリストを返す
    例: "岡本 卓也" -> ["岡本 卓也"]
    例: "鈴木 幸太郎, 金澤  靖" -> ["鈴木 幸太郎", "金澤 靖"]
    """
    if not teacher_str or teacher_str.strip() == '':
        return []

    # カンマで分割して前後の空白を除去
    teachers = [t.strip() for t in teacher_str.split(',')]
    # 空文字列を除外
    teachers = [t for t in teachers if t]
    return teachers


def parse_departments(department_str):
    """
    開講学科の文字列をパースして学科名のリストを返す
    例: "機械工学課程, 建築・都市システム学課程" -> ["機械工学課程", "建築・都市システム学課程"]
    """
    if not department_str or department_str.strip() == '':
        return []

    # カンマで分割して前後の空白を除去
    departments = [d.strip() for d in department_str.split(',')]
    # 空文字列を除外
    departments = [d for d in departments if d]
    return departments


def get_or_create_subject(subject_name):
    """科目マスタの取得または作成"""
    subject, created = Subject.objects.using('graphics').get_or_create(
        name=subject_name
    )
    if created:
        print(f"  [新規科目] {subject_name}")
    return subject


def get_or_create_teacher(teacher_name):
    """教員マスタの取得または作成"""
    teacher, created = Teacher.objects.using('graphics').get_or_create(
        name=teacher_name
    )
    if created:
        print(f"  [新規教員] {teacher_name}")
    return teacher


def map_department_to_system(department_name):
    """
    学科名を系に変換する

    機械 → 1系
    電気 → 2系
    情報 → 3系
    化学・環境 → 4系
    建築 → 5系
    その他 → None（登録しない）
    """
    # 系へのマッピング
    if '機械' in department_name:
        return '1系'
    elif '電気' in department_name or '電子' in department_name:
        return '2系'
    elif '情報' in department_name or '知能' in department_name:
        return '3系'
    elif '化学' in department_name or '生命' in department_name or '環境' in department_name:
        return '4系'
    elif '建築' in department_name or '都市' in department_name:
        return '5系'
    else:
        # その他の学科は登録しない
        return None


def get_or_create_department(department_name):
    """学科マスタの取得または作成（系にマッピング）"""
    # 学科名を系に変換
    system_name = map_department_to_system(department_name)

    if system_name is None:
        # 5つの系に該当しない場合はNoneを返す
        return None

    department, created = Department.objects.using('graphics').get_or_create(
        name=system_name
    )
    if created:
        print(f"  [新規学科] {system_name}")
    return department


def process_csv_file(csv_path, year):
    """
    CSVファイルを処理してデータベースに登録
    """
    print(f"\n処理中: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row_num, row in enumerate(reader, start=2):
            subject_name = row['科目名'].strip()
            teacher_str = row['担当教員'].strip()
            required_str = row['選択必須'].strip()
            semester = row['開講学期'].strip()
            department_str = row['開講学科'].strip()
            grade = row['開講年次'].strip()
            timetable_number = row.get('時間割番号', '').strip()
            numbering = row.get('ナンバリング', '').strip()

            # 必修かどうか
            is_required = (required_str == '必修')

            # 科目マスタの取得または作成
            subject = get_or_create_subject(subject_name)

            # 教員と学科を事前に処理
            teachers = parse_teachers(teacher_str)
            departments_str = parse_departments(department_str)

            # 学科オブジェクトを取得（5系に該当するもののみ）
            departments = []
            for dept_name in departments_str:
                department = get_or_create_department(dept_name)
                if department is not None:
                    departments.append(department)

            # 5つの系のいずれにも該当しない場合はスキップ
            if not departments:
                print(f"  [スキップ] {subject_name} ({year}年度, {semester}, {grade}) - 5つの系に該当しない")
                continue

            # 教員オブジェクトを取得
            teacher_objs = [get_or_create_teacher(t) for t in teachers]

            # 開講情報の重複チェック（科目、年度、学期、学年、選択必須、担当教員、学科が完全一致）
            existing = None
            candidates = CourseOffering.objects.using('graphics').filter(
                subject=subject,
                year=year,
                semester=semester,
                grade=grade,
                is_required=is_required
            )

            for candidate in candidates:
                # 担当教員が完全一致するか確認
                candidate_teachers = set(candidate.teachers.all())
                if candidate_teachers != set(teacher_objs):
                    continue

                # 学科が完全一致するか確認
                candidate_departments = set(candidate.departments.all())
                if candidate_departments != set(departments):
                    continue

                # 完全一致する開講情報が見つかった
                existing = candidate
                break

            if existing:
                # 完全に同じ開講情報が既に存在する場合は、時間割番号とナンバリングのみ更新
                if timetable_number:
                    existing.timetable_number = timetable_number
                if numbering:
                    existing.numbering = numbering
                existing.save()
                print(f"  [更新] {subject_name} ({year}年度, {semester}, {grade})")
            else:
                # 新規開講情報を作成
                course_offering = CourseOffering.objects.using('graphics').create(
                    subject=subject,
                    year=year,
                    semester=semester,
                    is_required=is_required,
                    grade=grade,
                    timetable_number=timetable_number if timetable_number else None,
                    numbering=numbering if numbering else None
                )

                # 教員を追加
                for teacher in teacher_objs:
                    course_offering.teachers.add(teacher)

                # 学科を追加
                for department in departments:
                    course_offering.departments.add(department)

                print(f"  [新規] {subject_name} ({year}年度, {semester}, {grade})")


def consolidate_grades():
    """
    科目名、担当教員、選択必須、開講学期、開講学科が一致し、学年だけが異なる開講情報を統合する
    例: 同じ条件でB3とB4 → B3, B4
    """
    print("\n" + "=" * 80)
    print("学年統合処理開始")
    print("=" * 80)

    # 全ての開講情報を取得
    all_offerings = CourseOffering.objects.using('graphics').all()

    # subject, year, semester, is_required でグループ化
    from collections import defaultdict
    grouped = defaultdict(list)

    for offering in all_offerings:
        key = (offering.subject.id, offering.year, offering.semester, offering.is_required)
        grouped[key].append(offering)

    consolidated_count = 0

    for key, offerings in grouped.items():
        if len(offerings) <= 1:
            # 1件しかない場合はスキップ
            continue

        # 担当教員と学科が完全に一致するグループを探す
        processed = set()

        for i, first in enumerate(offerings):
            if i in processed:
                continue

            first_teachers = set(first.teachers.all())
            first_departments = set(first.departments.all())

            # 統合可能なグループを探す
            to_merge = [first]
            to_merge_indices = [i]

            for j, other in enumerate(offerings):
                if j <= i or j in processed:
                    continue

                other_teachers = set(other.teachers.all())
                other_departments = set(other.departments.all())

                # 担当教員と学科が完全に一致するか確認
                if (first_teachers == other_teachers and
                    first_departments == other_departments):
                    to_merge.append(other)
                    to_merge_indices.append(j)

            if len(to_merge) <= 1:
                continue

            # 学年を統合（重複を除去）
            grades_set = set()
            for offering in to_merge:
                # カンマ区切りで複数学年が含まれている可能性があるため、分割して追加
                for grade in offering.grade.split(','):
                    grades_set.add(grade.strip())

            merged_grade = ', '.join(sorted(grades_set))

            # 最初のレコードに統合
            first.grade = merged_grade
            first.save()

            # 他のレコードを削除
            for other in to_merge[1:]:
                other.delete()

            # 処理済みとしてマーク
            for idx in to_merge_indices:
                processed.add(idx)

            consolidated_count += len(to_merge) - 1
            print(f"  [統合] {first.subject.name} ({first.year}年度, {first.semester}): {merged_grade}")

    print(f"\n統合完了: {consolidated_count}件の開講情報を統合")
    print("=" * 80)


def main():
    if len(sys.argv) < 2:
        print("使用方法: python build_course_db.py <csv_directory_path>")
        print("例: python build_course_db.py graphics/2025")
        sys.exit(1)

    csv_dir = sys.argv[1]
    csv_dir_path = Path(csv_dir)

    if not csv_dir_path.exists():
        print(f"エラー: ディレクトリが存在しません: {csv_dir}")
        sys.exit(1)

    # 年度をディレクトリ名から取得
    dir_name = csv_dir_path.name
    year_match = re.search(r'\d{4}', dir_name)
    if not year_match:
        print(f"エラー: ディレクトリ名から年度を取得できません: {dir_name}")
        sys.exit(1)

    year = int(year_match.group())
    print(f"年度: {year}")

    # CSVファイルを取得
    csv_files = list(csv_dir_path.glob('*.csv'))
    if not csv_files:
        print(f"エラー: CSVファイルが見つかりません: {csv_dir}")
        sys.exit(1)

    print(f"処理するCSVファイル数: {len(csv_files)}")

    # 各CSVファイルを処理
    for csv_file in csv_files:
        process_csv_file(csv_file, year)

    print("\n処理完了")

    # 学年統合処理を実行
    consolidate_grades()

    # 統計情報を表示
    print("\n=== データベース統計 ===")
    print(f"科目数: {Subject.objects.using('graphics').count()}")
    print(f"教員数: {Teacher.objects.using('graphics').count()}")
    print(f"学科数: {Department.objects.using('graphics').count()}")
    print(f"開講情報数: {CourseOffering.objects.using('graphics').count()}")


if __name__ == '__main__':
    main()
