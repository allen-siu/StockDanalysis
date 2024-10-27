from stock_analyzer.views.postgres_api import stock_data_query
from stock_analyzer.views.postgres_api import prediction_data_query

from sklearn.linear_model import LinearRegression

from datetime import timedelta, datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.backends.backend_pdf import PdfPages
from io import BytesIO


def predict_stock_data(symbol, predict_num_days):
    stock_data = stock_data_query.get_all_stock_data(symbol=symbol, date_desc=False)
    
    # Convert dates from str to date obj. Then convert dates to numerical value.
    # Transpose dates array to make it a 2d array
    dates = [datetime.strptime(stock['date'], "%Y-%m-%d").date() for stock in stock_data]
    dates = [date.toordinal() for date in dates]
    dates = np.array(dates).reshape(-1, 1)
    
    open_prices = np.array([stock['open'] for stock in stock_data])
    high_prices = np.array([stock['high'] for stock in stock_data])
    low_prices = np.array([stock['low'] for stock in stock_data])
    close_prices = np.array([stock['close'] for stock in stock_data])
    volumes = np.array([stock['volume'] for stock in stock_data])
    
    models = {
        'open': LinearRegression(),
        'high': LinearRegression(),
        'low': LinearRegression(),
        'close': LinearRegression(),
        'volume': LinearRegression(),
    }

    models['open'].fit(dates, open_prices)
    models['high'].fit(dates, high_prices)
    models['low'].fit(dates, low_prices)
    models['close'].fit(dates, close_prices)
    models['volume'].fit(dates, volumes)
    
    # Start from the day after most recent date and predict the next `predict_num_days` days
    most_recent_date = datetime.strptime(stock_data[-1]['date'], "%Y-%m-%d").date()
    
    future_dates = [(most_recent_date + timedelta(days=i)).toordinal() for i in range(1, predict_num_days + 1)]
    future_dates = np.array(future_dates).reshape(-1, 1)
    
    predictions = {
        'open': models['open'].predict(future_dates),
        'high': models['high'].predict(future_dates),
        'low': models['low'].predict(future_dates),
        'close': models['close'].predict(future_dates),
        'volume': models['volume'].predict(future_dates),
    }

    saved_predictions = prediction_data_query.save_predictions(
        symbol=symbol,
        model_type='Linear Regression',
        predict_num_days=predict_num_days,
        most_recent_date=most_recent_date,
        predictions=predictions
    )
    return saved_predictions


def generate_report(requested_predicted_data, all_predicted_data, all_actual_data):
    figs = generate_all_plots(all_predicted_data, all_actual_data)
    dataframe_fig = dataframe_to_figure(requested_predicted_data)
    
    pdf_buffer = BytesIO()
    with PdfPages(pdf_buffer) as pdf:
        pdf.savefig(dataframe_fig)
        for plot_statistic, fig in figs.items():
            pdf.savefig(fig)
            

    pdf_buffer.seek(0)
    return pdf_buffer
    

def dataframe_to_figure(requested_predicted_data):
    df = pd.DataFrame(requested_predicted_data)
    df = df.drop(columns=['id'])
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    
    return fig


def generate_all_plots(all_predicted_data, all_actual_data):
    options = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    plots = {}
    for opt in options:
        plots[opt] = generate_plot(all_predicted_data, all_actual_data, opt)
        
    return plots


def generate_plot(all_predicted_data, all_actual_data, prediction_plot_choice):
    preds = pd.DataFrame(all_predicted_data)
    actual = pd.DataFrame(all_actual_data)
    
    convert_str_to_date = lambda date_str: pd.to_datetime(date_str)
    preds['date'] = preds['date'].apply(convert_str_to_date)
    actual['date'] = actual['date'].apply(convert_str_to_date)
    
    # Take all predicted and actual values within a 30 day range. 30 days in past, 30 days in future
    actual = actual.tail(30)
    latest_date = actual['date'].max()
    preds =  preds[
        (preds['date'].isin(actual['date'])) |  # Dates in recent_actual
        ((preds['date'] > latest_date) & (preds['date'] <= latest_date + pd.Timedelta(days=30)))  # Dates within 30 days after the latest date in actual
    ]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    label_actual = 'Actual Volume' if prediction_plot_choice == 'Volume' else f'Actual {prediction_plot_choice} Prices'
    label_preds = 'Predicted Volume' if prediction_plot_choice == 'Volume' else f'Actual {prediction_plot_choice} Prices'
    
    ax.plot(actual['date'], actual[prediction_plot_choice.lower()], label=label_actual, marker='o', color='blue')
    ax.plot(preds['date'], preds[prediction_plot_choice.lower()], label=label_preds, marker='x', color='green')

    ax.set_xlabel('Date')
    
    y_axis_label = 'Volume' if prediction_plot_choice == 'Volume' else f'{prediction_plot_choice} Price'
    y_axis_title = 'Volume over Time' if prediction_plot_choice == 'Volume' else f'{prediction_plot_choice} Prices over Time'
    
    ax.set_ylabel(y_axis_label)
    ax.set_title(y_axis_title)
    ax.legend()
    ax.grid(True)

    plt.xticks(rotation=45)
    
    return fig
