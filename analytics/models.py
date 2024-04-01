from django.db import models
from django.contrib.auth import get_user_model


class Domain(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    # publish_key = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Report(models.Model):

    class Scope(models.TextChoices):
        DAY = "DAY", "Day"
        MONTH = "MONTH", "Month"
        YEAR = "YEAR", "Year"
        ALL = "ALL", "All"

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)

    start_date = models.DateField()
    scope = models.CharField(max_length=16, choices=Scope.choices)

    # date?

    browser = models.JSONField()
    country_code = models.JSONField()
    device_type = models.JSONField()
    platform = models.JSONField()
    hour = models.JSONField()
    language = models.JSONField()
    page = models.JSONField()
    referrer = models.JSONField()
    screen_size = models.JSONField()
    weekday_number = models.JSONField()
