from django.urls import path
from stock_analyzer.views import views

# api/
urlpatterns = [
    path('hello_world/', views.hello_world),
    path('get_stock_data/', views.get_stock_data),
    path('backtest_moving_average/', views.backtest_moving_average),
    path('predict_future_prices/linear_regression/', views.predict_future_prices),
    path("generate_prediction_report/", views.generate_prediction_report)
]
