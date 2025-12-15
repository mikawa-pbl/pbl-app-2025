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
    # 高校名は今後不要のため削除
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
    
# ★ ここから追加：ログイン用の Person モデル
class Person(models.Model):
    COURSE_CHOICES = [
        ("B", "学部"),
        ("M", "修士"),
        ("D", "博士"),
    ]

    student_id = models.CharField("学籍番号", max_length=20, unique=True)
    course = models.CharField("課程", max_length=1, choices=COURSE_CHOICES)
    grade = models.PositiveSmallIntegerField("学年")  # 1,2,3,...
    department_name = models.CharField("学科・専攻", max_length=50)  # 1系,2系... でもOK
    lab_field = models.CharField("研究分野", max_length=100)
    GENDER_CHOICES = [
        ("male", "男性"),
        ("female", "女性"),
        ("other", "その他"),
    ]
    gender = models.CharField("性別", max_length=10, choices=GENDER_CHOICES, blank=True)
    password = models.CharField("パスワード", max_length=128)
    
    # ユーザー設定
    nickname = models.CharField("ニックネーム", max_length=50, blank=True, default="")
    icon_picture = models.CharField("アイコン画像", max_length=200, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    # チュートリアル表示済みフラグ（各ページごと）
    seen_dept_tutorial = models.BooleanField("学科別企業一覧チュートリアル表示済み", default=False)
    seen_search_tutorial = models.BooleanField("企業検索チュートリアル表示済み", default=False)
    seen_points_tutorial = models.BooleanField("ポイントチュートリアル表示済み", default=False)
    # ポイント（初期値 10）
    points = models.IntegerField("ポイント", default=10)
    # お気に入り企業（多対多）。空でも良い
    favorites = models.ManyToManyField(
        'Company',
        related_name='favorited_by',
        verbose_name='お気に入り企業',
        blank=True,
    )

    class Meta:
        verbose_name = "学生"
        verbose_name_plural = "学生"

    def __str__(self):
        return f"{self.student_id} ({self.get_course_display()}{self.grade}年)"


class CompanyView(models.Model):
    """ユーザーが企業詳細を閲覧した履歴。重複を防いで1度だけポイントを消費するために使用する。"""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="views")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "企業閲覧履歴"
        verbose_name_plural = "企業閲覧履歴"
        unique_together = ("person", "company")

    def __str__(self) -> str:
        return f"{self.person.student_id} viewed {self.company.name} at {self.viewed_at.isoformat()}"


class SiteFeedback(models.Model):
    """サイトへの要望・フィードバック。投稿すると1ポイント付与される。"""
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="feedbacks")
    feedback_text = models.TextField("要望・フィードバック")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "サイト要望"
        verbose_name_plural = "サイト要望"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.person.student_id} のフィードバック ({self.created_at.date()})"