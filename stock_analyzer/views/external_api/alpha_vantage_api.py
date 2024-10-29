import os
import requests
from dotenv import load_dotenv


load_dotenv()


def get_time_series_daily(symbol, output_size='compact'):
    """This function queries the Alpha Vantage API to get the Time Series Daily
    of a given stock symbol

    Args:
        symbol (str): The symbol of the stock to be queries
        output_size (str): 'compact' or 'full' are accepted. Query param for the API call

    Returns:
        JsonObject: The unedited JSON response data from the API call
    """
    try:
        query_params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': output_size,
            'datatype': 'json',
            'apikey':  os.getenv('ALPHA_VANTAGE_API_KEY')
        }
        url = 'https://www.alphavantage.co/query'
        response = requests.get(url, params=query_params)
        data = response.json()
        
        if 'Error Message' in data:
            raise Exception('Invalid stock symbol. Please enter a valid stock symbol.')
        if 'Information' in data:
            raise Exception('Alpha Vantage rate limit reached. Only previously queried stock symbols can be analyzed.')
        
        return data

    except Exception as e:
        raise Exception(e.__str__()) from e
