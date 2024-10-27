from stock_analyzer.models.prediction_data import PredictionData
from stock_analyzer.serializers.prediction_data import PredictionDataSerializer

from datetime import timedelta


def get_all_prediction_data(symbol, model_type, date_desc=False):
    date_order = '' if not date_desc else '-'
        
    prediction_data = PredictionData.objects.filter(
        symbol=symbol, model_type=model_type
    ).order_by(f'{date_order}date')
    
    prediction_data_serializer = PredictionDataSerializer(prediction_data, many=True)
    return prediction_data_serializer.data


def save_predictions(symbol, model_type, predict_num_days, most_recent_date, predictions):
    for i in range(predict_num_days):
        prediction_date = most_recent_date + timedelta(days=i + 1)
        
        existing_prediction = PredictionData.objects.filter(
            symbol=symbol, 
            model_type=model_type,
            date=prediction_date
        ).exists()
        
        if existing_prediction:
            continue
            
        prediction = PredictionData(
            symbol=symbol,
            date=prediction_date,
            open=predictions['open'][i],
            high=predictions['high'][i],
            low=predictions['low'][i],
            close=predictions['close'][i],
            volume=predictions['volume'][i],
            model_type=model_type
        )
        prediction.save()


    start_date = most_recent_date + timedelta(days=1)
    end_date = start_date + timedelta(days=predict_num_days)
    
    prediction_data = PredictionData.objects.filter(
        symbol=symbol,
        date__range=(start_date, end_date)
    ).order_by('date')
    
    prediction_data_serializer = PredictionDataSerializer(prediction_data, many=True)
    return prediction_data_serializer.data
