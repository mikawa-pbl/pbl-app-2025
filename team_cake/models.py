from django.db import models

class Good(models.Model):
    name = models.CharField(max_length=100)
    # image = models.ImageField(upload_to='goods/')
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.price}"