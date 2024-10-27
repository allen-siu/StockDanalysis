from rest_framework import serializers
from stock_analyzer.models.prediction_data import PredictionData


class PredictionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionData
        fields = ['id', 'symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'model_type']