import uuid
from django.db import models

class Good(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    # image = models.ImageField(upload_to='goods/')
    price = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.price}"