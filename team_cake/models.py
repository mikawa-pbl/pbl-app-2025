import uuid
from django.db import models

class Good(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='goods_images/', blank=True, null=True)
    price = models.IntegerField()
    # optional description shown in templates
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.price}"