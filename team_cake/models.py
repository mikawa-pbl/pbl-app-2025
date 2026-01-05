import uuid
from django.db import models

class Good(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    # store only the filename of image saved under templates/teams/team_cake/images/
    image_filename = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    original_price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.price}"