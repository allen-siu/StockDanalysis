from django.db import models


class StockData(models.Model):
    symbol = models.TextField(max_length=50)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.IntegerField()
