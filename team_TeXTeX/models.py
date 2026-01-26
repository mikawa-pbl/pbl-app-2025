from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Groups(models.Model):
    title = models.CharField(max_length=100, verbose_name="グループ名")
    group_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name="グループID")

    def __str__(self):
        return self.title

class Slugs(models.Model):
    function_slug = models.CharField(max_length=50, unique=True, verbose_name="詳細ページ用スラッグ")
    slug_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name="スラッグID")

    def __str__(self):
        return self.function_slug

class Guides(models.Model):
    guide_content = models.TextField(verbose_name="説明文(HTML/Markdown)")
    guide_id = models.IntegerField(unique=True, null=True, blank=True, verbose_name="ガイドID")

    def __str__(self):
        return self.guide_content[:20]

class Users(models.Model):
    user_id = models.IntegerField(unique=True, verbose_name="ユーザーID")
    user = models.CharField(max_length=100, verbose_name="ユーザー名")

    def __str__(self):
        return self.user

class Contents(models.Model):
    group = models.ForeignKey(
        Groups,
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name="所属グループ"
    )
    slug = models.ForeignKey(
        Slugs,
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name="スラッグ"
    )
    guide = models.ForeignKey(
        Guides,
        on_delete=models.CASCADE,
        related_name='contents',
        verbose_name="ガイド"
    )
    name = models.CharField(max_length=100, verbose_name="項目名")
    tex_code = models.TextField(verbose_name="参照用TeXコード")

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=200, verbose_name="プロジェクト名")
    owner = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name="作成者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return self.name

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files', verbose_name="プロジェクト")
    filename = models.CharField(max_length=255, verbose_name="ファイル名")
    content = models.TextField(blank=True, null=True, verbose_name="テキスト内容")
    is_main = models.BooleanField(default=False, verbose_name="メインファイル")

    def __str__(self):
        return self.filename

class Favorites(models.Model):
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="ユーザー"
    )
    slug = models.ForeignKey(
        Slugs,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="スラッグ"
    )

    def __str__(self):
        return f"{self.user} - {self.slug}"
