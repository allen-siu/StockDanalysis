from stock_analyzer.models.stock_data import StockData
from stock_analyzer.views.external_api import alpha_vantage_api
from stock_analyzer.serializers.stock_data import StockDataSerializer

from datetime import datetime, date
from datetime import timedelta


def get_all_stock_data(symbol, date_desc=False):
    """This function queries the PostgresDB to retrieve all entries of a given stock symbol

    Args:
        symbol (str): The symbol of the stock to be queried

    Returns:
        dict: A dictionary representation of the stock data
    """
    try:
        refresh_data(symbol=symbol)
        
        date_order = '' if not date_desc else '-'
        
        stock_data = StockData.objects.filter(
            symbol=symbol).order_by(f'{date_order}date')
        
        stock_data_serializer = StockDataSerializer(stock_data, many=True)
        return stock_data_serializer.data
    
    except Exception as e:
        raise Exception(e.__str__()) from e


def get_stock_data_from_date_range(symbol, start_date, end_date=None, date_desc=False):
    """This function queries the PostgresDB to retrieve all entries of a given stock symbol
    starting from a given date to the most recent.

    Args:
        symbol (str): The symbol of the stock to be queried
        start_date (date): The lower bound date from which to start pulling entries
        end_date (date): The upper bound date on when to stop pulling entries
        sort_date (str): '' for ascending or '-' descending date order

    Returns:
        dict: A dictionary representation of the stock data
    """
    try:
        refresh_data(symbol=symbol)
        
        if end_date is None:
            end_date = date.today()
        
        date_order = '' if not date_desc else '-'
        
        stock_data_query_set = StockData.objects.filter(
            symbol=symbol, 
            date__range=(start_date, end_date)
        ).order_by(f'{date_order}date').values()
        
        stock_data_serializer = StockDataSerializer(stock_data_query_set, many=True)
        return stock_data_serializer.data
    
    except Exception as e:
        raise Exception(e) from e


def refresh_data(symbol):
    """This function queries the PostgresDB and checks if the most recent date for the
    given symbol is up to date. If it is not up to date or does not exist, fetch the
    stock data.

    Args:
        symbol (str): the symbol of the stock to be checked
    """
    try:
        most_recent_entry = StockData.objects.filter(symbol=symbol).order_by('-date').first()
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # If stock has no entries
        if not most_recent_entry:
            stock_data_json = alpha_vantage_api.get_time_series_daily(symbol=symbol, output_size='full')
            save_daily_stock_data(stock_data_json)
            
        # If stock has entries, but isn't up to date
        elif (most_recent_entry.date != today and most_recent_entry.date != yesterday):
            # print('getting here')
            # print(datetime.now())
            # print(timezone.now())
            # print(timezone.get_current_timezone())
            # print(most_recent_entry.date)
            # print(today)
            # print(yesterday)
            
            stock_data_json = alpha_vantage_api.get_time_series_daily(symbol=symbol, output_size='compact')
            save_daily_stock_data(stock_data_json)
            
    except Exception as e:
        raise Exception(e.__str__()) from e


def save_daily_stock_data(data):
    """This function takes the daily data of a certain stock symbol and parses it to create
    StockData objects to be written to the PostgresDB. Ignores duplicate `Symbol, Date` combinations.
    
    Args:
        data (JsonObject): The JSON response data from querying the Alpha Vantage Time Series Daily API
    """
    try:
        meta_data = data['Meta Data']
        time_series = data['Time Series (Daily)']
        
        symbol = meta_data['2. Symbol']
        
        for date_str, stock_data_json in time_series.items():
            # Only add entries with unique Symbol, Date combination
            # and entries that are within 2 years
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            two_years_ago = date.today() - timedelta(days=2*365)
            
            if (StockData.objects.filter(symbol=symbol, date=date).exists()
                or date < two_years_ago):
                break
            
            open = float(stock_data_json['1. open'])
            high = float(stock_data_json['2. high'])
            low = float(stock_data_json['3. low'])
            close = float(stock_data_json['4. close'])
            volume = int(stock_data_json['5. volume'])
            
            stock_data_obj = StockData(
                symbol=symbol,
                date=date,
                open=open,
                high=high,
                low=low,
                close=close,
                volume=volume
            )
            stock_data_obj.save()
            
    except Exception as e:
        raise Exception('Error saving stock data to database.') from e
