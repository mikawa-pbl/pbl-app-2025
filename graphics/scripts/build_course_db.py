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


def get_or_create_department(department_name):
    """学科マスタの取得または作成"""
    department, created = Department.objects.using('graphics').get_or_create(
        name=department_name
    )
    if created:
        print(f"  [新規学科] {department_name}")
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

            # 開講情報の重複チェック
            existing = CourseOffering.objects.using('graphics').filter(
                subject=subject,
                year=year,
                semester=semester,
                grade=grade
            ).first()

            if existing:
                # 既存の開講情報がある場合、教員と学科を追加
                teachers = parse_teachers(teacher_str)
                departments = parse_departments(department_str)

                # 時間割番号とナンバリングを更新
                if timetable_number:
                    existing.timetable_number = timetable_number
                if numbering:
                    existing.numbering = numbering
                existing.save()

                # 教員を追加
                for teacher_name in teachers:
                    teacher = get_or_create_teacher(teacher_name)
                    if teacher not in existing.teachers.all():
                        existing.teachers.add(teacher)

                # 学科を追加
                for dept_name in departments:
                    department = get_or_create_department(dept_name)
                    if department not in existing.departments.all():
                        existing.departments.add(department)

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
                teachers = parse_teachers(teacher_str)
                for teacher_name in teachers:
                    teacher = get_or_create_teacher(teacher_name)
                    course_offering.teachers.add(teacher)

                # 学科を追加
                departments = parse_departments(department_str)
                for dept_name in departments:
                    department = get_or_create_department(dept_name)
                    course_offering.departments.add(department)

                print(f"  [新規] {subject_name} ({year}年度, {semester}, {grade})")


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

    # 統計情報を表示
    print("\n=== データベース統計 ===")
    print(f"科目数: {Subject.objects.using('graphics').count()}")
    print(f"教員数: {Teacher.objects.using('graphics').count()}")
    print(f"学科数: {Department.objects.using('graphics').count()}")
    print(f"開講情報数: {CourseOffering.objects.using('graphics').count()}")


if __name__ == '__main__':
    main()
