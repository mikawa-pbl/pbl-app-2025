from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    memo = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name