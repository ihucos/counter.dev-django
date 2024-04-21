from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    prefs = models.JSONField(default=dict)
    uuid = models.UUIDField(null=True)

class DomainCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=16)
    date = models.DateField()
    dimension = models.CharField(max_length=16)
    member = models.CharField(max_length=16)
    count = models.PositiveIntegerField()
