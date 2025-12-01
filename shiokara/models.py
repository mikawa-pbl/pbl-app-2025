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
    url = models.URLField("企業サイトURL", blank=True)
    description = models.TextField("紹介文", blank=True)

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
