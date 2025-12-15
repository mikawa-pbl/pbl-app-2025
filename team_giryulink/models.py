# Create your models here.
from django.db import models


class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
