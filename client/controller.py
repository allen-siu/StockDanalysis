import os
import requests
import pandas as pd
import matplotlib.pyplot as plt

from dotenv import load_dotenv


load_dotenv()

HOST = os.getenv('DJANGO_HOST')
PORT = os.getenv('DJANGO_PORT')


def get_stock_data(stock_symbol):
    try:
        query_params = { 'symbol': stock_symbol }
        url = f'http://{HOST}:{PORT}/api/get_stock_data/'
        response = requests.get(url, params=query_params)
        
        if response.status_code != 200:
            raise Exception(response.json()['Error Message'])
        
        data = response.json()
        df = pd.DataFrame(data)
        df = df.drop(columns=['id'])
        
        return df
    except requests.RequestException as e:
        raise Exception('Network Error. Unable to connect to server.')
    except Exception as e:
        raise Exception(e.__str__()) from e


def simulate_investment(stock_symbol, initial_investment, buy_day_range, sell_day_range):
    try:
        query_params = {
            'symbol': stock_symbol, 
            'initial_investment': initial_investment, 
            'buy_day_range': buy_day_range, 
            'sell_day_range': sell_day_range
        }
        url = f'http://{HOST}:{PORT}/api/backtest_moving_average/'
        response = requests.get(url, params=query_params)
        investment_log_data = response.json()
        
        df = pd.DataFrame(investment_log_data)
        total_return = df['return'].iloc[-1]
        num_trades = df['action'].isin(['Buy', 'Sell']).sum()
        
        simulation_data = {
            'dataframe': df,
            'num_trades': num_trades,
            'total_return': total_return,
            'max_drawdown': 0
        }
        return simulation_data
    
    except requests.RequestException as e:
        raise Exception('Network Error. Unable to connect to server.')


def predict_future_stock_prices(symbol, num_days=30, model_type='Linear Regression'):
    try:
        query_params = {
            'symbol': symbol,
            'num_days': num_days,
            'model_type': model_type
        }
        
        url = f'http://{HOST}:{PORT}/api/predict_future_prices/linear_regression/'
        response = requests.get(url, params=query_params)
        
        data = response.json()
        
        requested_predictions = data['requested_predicted_data']
        all_predicted_data = data['all_predicted_data']
        all_actual_data = data['all_actual_data']
        
        requested_predictions_df = pd.DataFrame(requested_predictions)
        requested_predictions_df = requested_predictions_df.drop(columns=['id'])
        
        all_predictions_df = pd.DataFrame(all_predicted_data)
        all_predictions_df = all_predictions_df.drop(columns=['id'])
        
        all_actual_df = pd.DataFrame(all_actual_data)
        all_actual_df = all_actual_df.drop(columns=['id'])
        
        dataframes = {
            'requested_predicted_data': requested_predictions_df,
            'all_predicted_data': all_predictions_df,
            'all_actual_data': all_actual_df
        }
        
        return dataframes
    
    except requests.RequestException as e:
        raise Exception('Network Error. Unable to connect to server.')


def create_prediction_plot_figure(prediction_dataframes, prediction_plot_choice):
    preds = prediction_dataframes['all_predicted_data']
    actual = prediction_dataframes['all_actual_data']
    
    convert_str_to_date = lambda date_str: pd.to_datetime(date_str)
    preds['date'] = preds['date'].apply(convert_str_to_date)
    actual['date'] = actual['date'].apply(convert_str_to_date)
    
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


def download_pdf(symbol, num_days=30, model_type='Linear Regression'):
    try:
        query_params = {
            'symbol': symbol,
            'num_days': num_days,
            'model_type': model_type
        }
        
        url = f'http://{HOST}:{PORT}/api/generate_prediction_report/'
        response = requests.get(url, params=query_params)
        
        return response.content
    
    except requests.RequestException as e:
        raise Exception('Unable to retrieve PDF content download. Network Error. Unable to connect to server.')
