from django.db import models

# Create your models here.
class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Paper(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    year = models.IntegerField()
    booktitle = models.CharField(max_length=200)
    url = models.URLField()
    doi = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} {self.author} {self.year}"