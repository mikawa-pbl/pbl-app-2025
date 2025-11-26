from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Main(models.Model):
    pass

class main_select(models.Model):
    pass

class url(models.Model):
    pass

class Editer(models.Model):
    pass

class Group(models.Model):
    title = models.CharField(max_length=100, verbose_name="グループ名")

    def __str__(self):
        return self.title

class Content(models.Model):
    # どのグループに属するか (Groupへの外部キー)
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="所属グループ"
    )
    name = models.CharField(max_length=100, verbose_name="項目名")
    # ガイドページへのURLを構築するためのスラッグ
    function_slug = models.CharField(max_length=50, unique=True, verbose_name="詳細ページ用スラッグ")
    # コピーされるTeXコード (機能維持のため)
    tex_code = models.TextField(verbose_name="参照用TeXコード")
    # ガイドページに表示する詳細コンテンツ
    guide_content = models.TextField(verbose_name="説明文(HTML/Markdown)")

    def __str__(self):
        return f"[{self.group.title}] {self.name}"
