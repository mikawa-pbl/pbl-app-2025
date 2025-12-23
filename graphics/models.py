from django.db import models
import uuid

# Create your models here.

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Subject(models.Model):
    """
    科目マスタ
    年度が変わっても変動しない科目情報を管理
    """
    name = models.CharField(max_length=200, unique=True, verbose_name="科目名")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "科目"
        verbose_name_plural = "科目"


class Teacher(models.Model):
    """
    教員マスタ
    教員情報を管理
    """
    name = models.CharField(max_length=200, unique=True, verbose_name="教員名")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "教員"
        verbose_name_plural = "教員"


class Department(models.Model):
    """
    学科マスタ
    学科情報を管理
    """
    name = models.CharField(max_length=200, unique=True, verbose_name="学科名")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "学科"
        verbose_name_plural = "学科"


class CourseOffering(models.Model):
    """
    開講情報
    年度、担当教員、学期など年ごとに変わる情報を管理
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="科目")
    year = models.IntegerField(verbose_name="年度")
    semester = models.CharField(max_length=50, verbose_name="開講学期")
    is_required = models.BooleanField(default=False, verbose_name="必修フラグ")
    grade = models.CharField(max_length=20, verbose_name="開講年次")
    timetable_number = models.CharField(max_length=50, null=True, blank=True, verbose_name="時間割番号")
    numbering = models.CharField(max_length=50, null=True, blank=True, verbose_name="ナンバリング")
    teachers = models.ManyToManyField(Teacher, verbose_name="担当教員")
    departments = models.ManyToManyField(Department, verbose_name="開講学科")

    def __str__(self):
        return f"{self.subject.name} ({self.year}年度, {self.semester}, {self.grade})"

    class Meta:
        verbose_name = "開講情報"
        verbose_name_plural = "開講情報"


class SubjectReview(models.Model):
    """
    科目レビューモデル
    科目そのものに対するレビュー
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, verbose_name="開講情報")
    review = models.TextField(max_length=500, verbose_name="レビュー")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "科目レビュー"
        verbose_name_plural = "科目レビュー"

    def __str__(self):
        return f"{self.course_offering} - {self.review[:50]}"


class BookReview(models.Model):
    """
    参考書レビューモデル
    科目ごとにおすすめの参考書をユーザが投稿できる
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="開講情報")
    subject = models.CharField(max_length=50, blank=True, verbose_name="科目名")
    isbn = models.CharField(max_length=50, verbose_name="ISBN")
    title = models.CharField(max_length=200, verbose_name="書籍タイトル", null=True, blank=True)
    author = models.CharField(max_length=200, verbose_name="著者", null=True, blank=True)
    publication_date = models.CharField(max_length=20, verbose_name="発行日", null=True, blank=True)
    review = models.TextField(max_length=200, verbose_name="レビュー")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "参考書レビュー"
        verbose_name_plural = "参考書レビュー"

    def __str__(self):
        if self.course_offering:
            return f"{self.course_offering.subject.name} - ISBN:{self.isbn}"
        return f"{self.subject} - ISBN:{self.isbn}"