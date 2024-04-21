from django.db import models
from django.db.models import F
from django.db.models.functions import Concat, Cast
from django.contrib.auth import get_user_model

class UserData(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    uuid = models.UUIDField(unique=True)

class Domain(models.Model):
    class Meta:
        unique_together = [["user", "name"]]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    # publish_key = models.CharField(max_length=64)
    # published = models.BooleanField()

    def query_counts(self, start_date, end_date):
        pass

    def __str__(self):
        return self.name


class DomainCount(models.Model):
    # class Meta:
    #     unique_together = [["domain", "date", "dimension", "member"]]

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    date = models.DateField()
    dimension = models.CharField(max_length=16)
    member = models.CharField(max_length=16)
    count = models.PositiveIntegerField()
