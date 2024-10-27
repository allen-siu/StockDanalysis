from rest_framework import serializers
from stock_analyzer.models.stock_data import StockData


class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = ['id', 'symbol', 'date', 'open', 'high', 'low', 'close', 'volume']