from django.db import models

# Create your models here.
class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Building(models.Model):
    name = models.CharField("建物名", max_length=50)

    def __str__(self):
        return self.name


class Professor(models.Model):
    name = models.CharField("教授名", max_length=50)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField("属性名", max_length=50)

    def __str__(self):
        return self.name


class Classroom(models.Model):
    building = models.ForeignKey(
        Building,
        verbose_name="建物",
        on_delete=models.CASCADE,
        related_name="classrooms",
    )
    room_name = models.CharField("部屋名", max_length=50)
    floor = models.CharField("階", max_length=50)
    professor = models.ForeignKey(
        Professor,
        verbose_name="担当教授",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classrooms",
    )
    # 属性タグ（中間テーブル）を通した ManyToMany
    attributes = models.ManyToManyField(
        Attribute,
        verbose_name="属性",
        through="ClassroomAttribute",
        related_name="classrooms",
        blank=True,
    )
    
    SIZE_CHOICES = (
        ("L", "大"),
        ("M", "中"),
        ("S", "小"),
    )
    size = models.CharField(
        "サイズ",
        max_length=1,
        choices=SIZE_CHOICES,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.room_name} ({self.building.name})"



class ClassroomAttribute(models.Model):
    """属性タグ: 教室と属性の中間テーブル"""

    classroom = models.ForeignKey(
        Classroom,
        verbose_name="教室",
        on_delete=models.CASCADE,
    )
    attribute = models.ForeignKey(
        Attribute,
        verbose_name="属性",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ("classroom", "attribute")

    def __str__(self):
        return f"{self.classroom} - {self.attribute}"
