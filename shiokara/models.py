from django.db import models


class Department(models.Model):
    """学科"""
    name = models.CharField("学科名", max_length=50)
    short_name = models.CharField(
        "URL用スラッグ",
        max_length=20,
        unique=True,
        help_text="URLで使う短い名前（例: cs, ee など）",
    )

    class Meta:
        verbose_name = "学科"
        verbose_name_plural = "学科"

    def __str__(self) -> str:
        return self.name


class Company(models.Model):
    """企業"""
    name = models.CharField("企業名", max_length=100)
    url = models.URLField("企業サイトURL", blank=True, null=True)
    description = models.TextField("紹介文", blank=True,null=True)
    area = models.CharField("勤務地域", max_length=200, blank=True, null=True)
    avg_annual_income = models.IntegerField("平均年収（万円）", blank=True, null=True)
    starting_salary = models.IntegerField("初任給（万円）", blank=True, null=True)
    annual_holidays = models.IntegerField("年間休日数", blank=True, null=True)
    employees = models.IntegerField("従業員数", blank=True, null=True)
    internship_acceptance = models.CharField("インターン受け入れ", max_length=20, blank=True, null=True)
    hiring_quota = models.CharField("採用目安", max_length=100, blank=True, null=True)
    selection_process = models.TextField("選考プロセス", blank=True, null=True)
    accepts_jitsumu_kunren = models.BooleanField("実務訓練受け入れ", default=False)
    tut_recommendation = models.BooleanField("技科大推薦", default=False)
    oncampus_briefing = models.CharField("説明会対象分野", max_length=100, blank=True, null=True)

    # 1社が複数学科向けという想定（多対多）
    departments = models.ManyToManyField(
        Department,
        related_name="companies",
        verbose_name="対象学科",
    )

    class Meta:
        verbose_name = "企業"
        verbose_name_plural = "企業"

    def __str__(self) -> str:
        return self.name

class CompanyReview(models.Model):
    """企業ごとの口コミ"""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="企業",
    )

    grade = models.CharField("学年", max_length=20, blank=True)
    department_name = models.CharField("学科", max_length=50, blank=True)
    lab_field = models.CharField("分野（研究室）", max_length=100, blank=True)

    GENDER_CHOICES = [
        ("male", "男性"),
        ("female", "女性"),
        ("other", "その他"),
        ("no_answer", "回答しない"),
    ]
    gender = models.CharField(
        "性別",
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
    )

    high_school = models.CharField("高校名", max_length=100, blank=True)
    comment = models.TextField("自由記述欄", blank=True)

    RATING_CHOICES = [(i, f"{i}") for i in range(1, 6)]
    rating = models.PositiveSmallIntegerField(
        "評価（★1〜5）",
        choices=RATING_CHOICES,
    )

    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = "企業口コミ"
        verbose_name_plural = "企業口コミ"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company.name} の口コミ（★{self.rating}）"