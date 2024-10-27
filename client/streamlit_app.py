# from controller import create_prediction_plot_figure, get_stock_data, simulate_investment, predict_future_stock_prices
import controller

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'simulation_data' not in st.session_state:
    st.session_state.simulation_dataframe = None
if 'prediction_dataframes' not in st.session_state:
    st.session_state.prediction_dataframes = None
if 'prediction_pdf_content' not in st.session_state:
    st.session_state.prediction_pdf_content = None


def reset():
    st.session_state.stock_data = None
    st.session_state.simulation_dataframe = None


st.title('Stock Analyzer')

stock_symbol = st.text_input(label='Enter a stock (e.g IBM, AAPL):', on_change=reset)
if stock_symbol is not None:
    stock_symbol = stock_symbol.upper()

if st.button(label='Retrieve Stock Data'):
    # do api call to django server to get data
    st.write(f'Retrieving {stock_symbol} stock data...')
    
    try:
        dataframe = controller.get_stock_data(stock_symbol)
        st.session_state.stock_data = dataframe
    except Exception as e:
        st.session_state.stock_data = None
        st.error(e.__str__())
    
    

if st.session_state.stock_data is not None:
    st.subheader(f'{stock_symbol} Stock Data Over Past 2 Years')
    st.write(st.session_state.stock_data)

    # Left side is backtest, right side ML prediction
    left_col, right_col = st.columns([1, 1])

    display_option = ['Simulate an Investment Strategy', 'Predict Future Stock Values']
    display_type = st.selectbox(label='Select an option', options=display_option, index=None)

    ############## Left Side ########################
    if display_type == 'Simulate an Investment Strategy':
        # Open Backtesting after initial button has been pressed
        st.title('Simulate an Investment Strategy')

        initial_investment = st.slider(label='Initial Investment', min_value=1, max_value=100_000)

        buy_day_range = st.slider(
            label='Buy IBM shares when price dips below the x-day moving average.', 
            min_value=1, max_value=200
        )

        sell_day_range = st.slider(
            label='Sell IBM shares when the price goes above the x-day moving average.', 
            min_value=1, max_value=200
        )

        if st.button(label='Simulate Investment Over Previous 2 Years'):
            st.write(f"Buy Threshold: {buy_day_range}-day moving average")
            st.write(f"Sell Threshold: {sell_day_range}-day moving average")
            
            with st.empty():
                st.write(f'Simulating ${initial_investment} investment over previous 2 years...')
                try:
                    simulation_data = controller.simulate_investment(
                        stock_symbol,
                        initial_investment,
                        buy_day_range,
                        sell_day_range
                    )
                    st.session_state.simulation_dataframe = simulation_data['dataframe']
                    st.session_state.simulation_num_trades = simulation_data['num_trades']
                    st.session_state.simulation_total_return = simulation_data['total_return']
                    st.session_state.simulation_max_drawdown = simulation_data['max_drawdown']
                
                except Exception as e:
                    st.session_state.simulation_dataframe = None
                    st.error(e.__str__())
                
        
        if st.session_state.simulation_dataframe is not None:
            st.subheader('Investment Logs')
            st.write(st.session_state.simulation_dataframe)
            st.write(f'Total Return: {st.session_state.simulation_total_return}')
            st.write(f'Number of Trades Performed: {st.session_state.simulation_num_trades}')
            st.write(f'Max Drawdown: {st.session_state.simulation_max_drawdown}')
            
    ############## End Left Side ########################
    
    
    
    
    
    ############## Right Side ###########################
    elif display_type == 'Predict Future Stock Values':
        
        st.title('Predict Future Stock Values')
        
        model_types = ['Linear Regression']
        model_selected = st.selectbox(label='Select a model', options=model_types, index=None)
    
        if model_selected is not None:
            
            num_days = st.slider(
                label='Number of Days to Predict',
                min_value=1, max_value=30
            )
            
            if st.button('Predict'):
                st.write('Calculating Predictions...')
                try:
                    prediction_dataframes = controller.predict_future_stock_prices(
                        symbol=stock_symbol,
                        num_days=num_days,
                        model_type=model_selected
                    )
                    st.session_state.prediction_dataframes = prediction_dataframes
                
                except Exception as e:
                    st.session_state.prediction_dataframes = None
                    st.error(e.__str__())
                
                try:
                    pdf_content = controller.download_pdf(
                        symbol=stock_symbol,
                        num_days=num_days,
                        model_type=model_selected
                    )
                    st.session_state.prediction_pdf_content = pdf_content
                
                except Exception as e:
                    st.session_state.prediction_dataframes = None
                    st.error(e.__str__())
        
        
        if st.session_state.prediction_dataframes is not None:
            st.subheader('Predicted Values')
            st.write(st.session_state.prediction_dataframes['all_actual_data'])
            
            # Create plots
            prediction_plot_options = ['Open', 'High', 'Low', 'Close', 'Volume']
            prediction_plot_choice = st.selectbox(
                label='Select a metric to plot', options=prediction_plot_options, index=None
            )
            
            if prediction_plot_choice is not None:
                fig = controller.create_prediction_plot_figure(st.session_state.prediction_dataframes, prediction_plot_choice)
                st.pyplot(fig)
                    
                if st.session_state.prediction_pdf_content is not None:
                    st.subheader('Download Table and All Plots as PDF')
                    st.download_button(
                        label="Download PDF",
                        data=st.session_state.prediction_pdf_content,
                        file_name="report.pdf",
                        mime="application/pdf"
                    )

                
    
    ############## End Right Side ########################
