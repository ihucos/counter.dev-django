from django.db import models
from django.contrib.auth import get_user_model


class Domain(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    # publish_key = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Report(models.Model):
    class Range(models.TextChoices):
        DAY = "DAY", "Day"
        MONTH = "MONTH", "Month"
        YEAR = "YEAR", "Year"
        INFINITY = "INFINITY", "Infinity"

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    start_date = models.DateField()
    range = models.CharField(max_length=16, choices=Range.choices)
    data = models.JSONField()


class ReportUpdate(models.Model):
    user_identify = models.CharField(max_length=16)
    domain = models.CharField(max_length=16)
    time_slot = models.DateTimeField() # clocked 15 minutes
    dimension = models.CharField(max_length=16)
    member = models.CharField(max_length=16)
    count = models.PositiveIntegerField()

# class ReportDataPoint(models.Model):
#     class Dimension(Range):
#         browser = "BROWSER", "browser"
#         country_code = "COUNTRY_CODE", "Country code"
#         device_type = "DEVICE_TYPE", "Device type"
#         platform = "PLATFORM", "Platform"
#         hour = "HOUR", "Hour"
#         language = "LANGUAGE", "Language"
#         page = "PAGE", "Page"
#         referrer = "REFERRER", "Referrer"
#         screen_size = "SCREEN_SIZE", "Screen size"
#         weekday_number = "WEEKDAY_NUMBER", "Weekday number"
#         counter = "COUNTER", "Counter"
#
#     report = models.ForeignKey(Report, on_delete=models.CASCADE)
#     dimension = models.CharField(max_length=16, choices=Dimension.choices)
#     member = models.CharField(max_length=16)
#     count = models.PositiveIntegerField()


# class ReportDimension(models.Model):
#
#
#     class Dimension(Range):
#         browser = "BROWSER", "browser"
#         country_code = "COUNTRY_CODE", "Country code"
#         device_type = "DEVICE_TYPE", "Device type"
#         platform = "PLATFORM", "Platform"
#         hour = "HOUR", "Hour"
#         language = "LANGUAGE", "Language"
#         page = "PAGE", "Page"
#         referrer = "REFERRER", "Referrer"
#         screen_size = "SCREEN_SIZE", "Screen size"
#         weekday_number = "WEEKDAY_NUMBER", "Weekday number"
#         counter = "COUNTER", "Counter"
#
#     report = models.ForeignKey(Report, on_delete=models.CASCADE)
#     metric = models.CharField(max_length=16, choices=Dimension.choices)
#
# class ReportDimensionData(models.Model):
#     report_metric = models.ForeignKey(ReportDimension, on_delete=models.CASCADE)
#     member = models.CharField(max_length=16)
#     count = models.PositiveIntegerField()

# # date?
#
# browser = models.JSONField()
# country_code = models.JSONField()
# device_type = models.JSONField()
# platform = models.JSONField()
# hour = models.JSONField()
# language = models.JSONField()
# page = models.JSONField()
# referrer = models.JSONField()
# screen_size = models.JSONField()
# weekday_number = models.JSONField()
# counted_items = models.JSONField()


# # Stays in memory
# class ReportUpdate(models.Model):
#     user_identify = models.CharField(max_length=16)
#     domain = models.CharField(max_length=16)
#     time_slot = models.DateTimeField() # clocked 15 minutes
#
#     browser = models.JSONField()
#     country_code = models.JSONField()
#     device_type = models.JSONField()
#     platform = models.JSONField()
#     hour = models.JSONField()
#     language = models.JSONField()
#     page = models.JSONField()
#     referrer = models.JSONField()
#     screen_size = models.JSONField()
#     weekday_number = models.JSONField()
#     counters = models.JSONField()

# @property
# def date(self):
#     tz = self.resolve_user().timezone
#     tz = self.resolve_domain().timezone
#     blah resolve from slot
#
# def migrate_to_main_db(self):
#     pass
