from django.contrib import admin
from stock_analyzer.models.stock_data import StockData
from stock_analyzer.models.prediction_data import PredictionData

# Register your models here.

admin.site.register(StockData)
admin.site.register(PredictionData)
