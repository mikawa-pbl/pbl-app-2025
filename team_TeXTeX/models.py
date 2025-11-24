from django.db import models

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Main(models.Model):
    pass

class Temp(models.Model):
    pass

class url(models.Model):
    pass

class main_select(models.Model):
    pass