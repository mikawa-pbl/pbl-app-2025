from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class MyPage(models.Model):
    # 基本情報
    name = models.CharField(max_length=100, verbose_name="名前")
    icon = models.ImageField(upload_to='icons/', blank=True, null=True, verbose_name="アイコン")
    user_id = models.CharField(max_length=100, unique=True, verbose_name="ユーザID")
    email = models.EmailField(max_length=100, verbose_name="メアド")
    password = models.CharField(max_length=100, verbose_name="パスワード")
    
    # プロフィール情報
    grade_department = models.CharField(max_length=100, verbose_name="学年学科")
    age = models.IntegerField(verbose_name="年齢")
    gender = models.CharField(max_length=100, verbose_name="性別")
    club = models.CharField(max_length=100, blank=True, null=True, verbose_name="所属サークル")
    one_word = models.TextField(blank=True, null=True, verbose_name="一言")
    github_account = models.CharField(max_length=100, blank=True, null=True, verbose_name="githubアカウント")
    hobby = models.CharField(max_length=200, blank=True, null=True, verbose_name="趣味")
    birthplace = models.CharField(max_length=100, blank=True, null=True, verbose_name="出身")
    birth_date = models.DateField(verbose_name="誕生日")
    relationship_status = models.CharField(max_length=100, blank=True, null=True, verbose_name="交際ステータス")

    def __str__(self):
        return self.name # ページの名前がその人の名前になる