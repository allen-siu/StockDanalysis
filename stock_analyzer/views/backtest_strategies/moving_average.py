from stock_analyzer.views.postgres_api import stock_data_query

from datetime import timedelta, date
import pandas as pd


def simulate_moving_average_strategy(symbol, initial_investment, buy_day_range, sell_day_range):
    """This function simulates the buying and selling of the given stock symbol using
    the moving average strategy. Using the initial investment and all future returns,
    we use all our held cash to buy if the current price is below the buy moving average 
    (average price of the previous buy_day_range days) and sell all inventory if the current 
    price is below the sell moving average (average price of previous sell_day_range days).

    Args:
        symbol (str): The stock symbol the strategy will be performed on
        initial_investment (float): The amount of initial cash to start with
        buy_day_range (int): The window size of your buy moving average
        sell_day_range (int): The window size of your sell moving average

    Returns:
        dict[]: The 
    """
    stock_dataframe = build_dataframe(symbol, buy_day_range, sell_day_range)
    
    # Simulate the strategy
    cash = initial_investment
    stock_holdings = 0
    total_value = initial_investment
    
    log_data = []
    
    for i in range(len(stock_dataframe)):
        current_date = stock_dataframe.iloc[i]['date']
        current_price = stock_dataframe.iloc[i]['price']
        buy_threshold = stock_dataframe.iloc[i]['buy_moving_average']
        sell_threshold = stock_dataframe.iloc[i]['sell_moving_average']
        
        action = 'Hold'
        
        # Go to next day when not enough data to have a moving average yet
        if buy_threshold is not None and sell_threshold is not None:
            # Check if can buy and invest all cash
            if current_price < buy_threshold and cash > 0:
                stock_holdings = cash / current_price
                cash = 0
                action = 'Buy'
                print(f"Bought on {current_date} at {current_price}")
            
            # Check if can sell and sell all holdings
            elif current_price > sell_threshold and stock_holdings > 0:
                cash = stock_holdings * current_price
                stock_holdings = 0
                action = 'Sell'
                print(f"Sold on {current_date} at {current_price}")
                
            
        # Update total portfolio value (cash + stock value)
        total_value = cash + (stock_holdings * current_price if stock_holdings > 0 else 0)
        
        log_data.append({
            'symbol': symbol,
            'date': current_date,
            'action': action,
            'price': current_price,
            'cash': cash,
            'stock_holdings': stock_holdings,
            'total_value': total_value,
            'return': total_value - initial_investment
        })

    # At the end of the period, sell any remaining stock at the last day's price
    if stock_holdings > 0:
        final_price = stock_dataframe.iloc[-1]['price']
        cash = stock_holdings * final_price
        stock_holdings = 0
        
        log_data.append({
            'symbol': symbol,
            'date': stock_dataframe.iloc[-1]['date'],
            'action': "Sell",
            'price': final_price,
            'cash': cash,
            'stock_holdings': stock_holdings,
            'total_value': cash,
            'return': total_value - initial_investment
        })
        print(f"Sold remaining stock on {stock_dataframe.iloc[-1]['date']} at {final_price}")


    # Final total value
    total_value = cash
    print(f"Total return after 2 years: {total_value - initial_investment}")
    return log_data
    

def build_dataframe(symbol, buy_day_range, sell_day_range, num_days=2*365):
    """Builds the dataframe calculating the buy and sell moving averages
    and the price of a given stock symbol for every day from today to
    num_days ago.

    Args:
        symbol (str): The stock to be calculated on
        buy_day_range (int): The number of days your window size will be for the buy moving average
        sell_day_range (int): The number of days your window size will be for the sell moving average
        num_days (int, optional): The number of days ago you want to start the simulation from. Defaults to 2*365 (2 years).

    Returns:
        pandas.DataFrame: A Pandas dataframe with the stock data and the day price, buy moving average,
                          and sell moving average added as columns.
    """
    today = date.today()
    two_years_ago = today - timedelta(days=num_days)
    
    stock_data = stock_data_query.get_stock_data_from_date_range(
        symbol=symbol,
        start_date=two_years_ago,
        end_date=today,
        date_desc=False
    )
    
    df = pd.DataFrame(stock_data)
    df = df.sort_values('date')
    
    # Using (open + close) / 2 as the stock value for the given day
    df['price'] = (df['open'] + df['close']) / 2    
    df['buy_moving_average'] = df['price'].rolling(window=buy_day_range).mean()
    df['sell_moving_average'] = df['price'].rolling(window=sell_day_range).mean()
    
    return df
