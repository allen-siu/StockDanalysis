from django.http import HttpResponse, JsonResponse

from stock_analyzer.views.postgres_api import stock_data_query
from stock_analyzer.views.postgres_api import prediction_data_query
from stock_analyzer.views.backtest_strategies import moving_average
from stock_analyzer.views.data_prediction_models import linear_regression


def get_stock_data(request):
    try:
        symbol = request.GET.get('symbol').upper()
        
        stock_data = stock_data_query.get_all_stock_data(symbol=symbol, date_desc=True)

        response = JsonResponse(data=stock_data, safe=False)
        response.status_code = 200

    except Exception as e:
        response = JsonResponse(data={ 'Error Message': e.__str__ ()}, safe=False)
        response.status_code = 400
        
    return response
    
    
def backtest_moving_average(request):
    symbol = request.GET.get('symbol').upper()
    initial_investment = int(request.GET.get('initial_investment'))
    buy_day_range = int(request.GET.get('buy_day_range'))
    sell_day_range = int(request.GET.get('sell_day_range'))
    
    investment_log_data = moving_average.simulate_moving_average_strategy(
        symbol, initial_investment, buy_day_range, sell_day_range
    )
    
    response = JsonResponse(investment_log_data, safe=False)
    return response
    
    
def predict_future_prices(request):
    symbol = request.GET.get('symbol').upper()
    num_days = int(request.GET.get('num_days'))
    model_type = request.GET.get('model_type')
    
    requested_predicted_data = linear_regression.predict_stock_data(symbol=symbol, predict_num_days=num_days)
    all_predicted_data = prediction_data_query.get_all_prediction_data(symbol=symbol, model_type=model_type)
    all_actual_data = stock_data_query.get_all_stock_data(symbol=symbol, date_desc=False)
    
    data = {
        'requested_predicted_data': requested_predicted_data,
        'all_predicted_data': all_predicted_data,
        'all_actual_data': all_actual_data
    }
    response = JsonResponse(data, safe=False)
    return response
    

def generate_prediction_report(request):
    symbol = request.GET.get('symbol').upper()
    num_days = int(request.GET.get('num_days'))
    model_type = request.GET.get('model_type')

    requested_predicted_data = linear_regression.predict_stock_data(symbol=symbol, predict_num_days=num_days)
    all_predicted_data = prediction_data_query.get_all_prediction_data(symbol=symbol, model_type=model_type)
    all_actual_data = stock_data_query.get_all_stock_data(symbol=symbol, date_desc=False)
    
    pdf_buffer = linear_regression.generate_report(requested_predicted_data, all_predicted_data, all_actual_data)
    
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="prediction_report.pdf"'
    return response

