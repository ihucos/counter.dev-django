from django.db import models
from django.contrib.auth import get_user_model


class Domain(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    # publish_key = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class DomainStat(models.Model):

    # user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)

    date = models.DateField()
    dimension = models.CharField(max_length=16)
    member = models.CharField(max_length=16)
    count = models.PositiveIntegerField()
