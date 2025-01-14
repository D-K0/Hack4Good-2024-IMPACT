from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from arch import arch_model
import pmdarima as pm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from set_up.constants import PRODUCTS_LABELS
from calculate_meb import generate_average_meb

log = logging.getLogger(__name__)  # Logger for this module


# Function to automatically determine ARIMA parameters
def find_arima_parameters(series, seasonal=False):
    """
    Find the best ARIMA (p, d, q) parameters for a time series using auto_arima.
    :param series: Time series data
    :return: List of ARIMA parameters [p, d, q]
    """
    auto_arima_model = pm.auto_arima(series, stepwise=False, seasonal=False)
    if seasonal:
        auto_arima_model = pm.auto_arima(series, stepwise=False, seasonal=True, m=12)
        return auto_arima_model.order, auto_arima_model.seasonal_order
    else:
        auto_arima_model = pm.auto_arima(series, stepwise=False, seasonal=False)
        return auto_arima_model.order

# Function to get the best GARCH parameters
def get_best_garch_params(data, max_p=5, max_q=5):
    """
    Automatically select the best GARCH(p, q) parameters based on AIC.
    :param data: Time series data
    :param max_p: Maximum value of p to search
    :param max_q: Maximum value of q to search
    :return: Best (p, q) parameters
    """
    best_aic = np.inf
    best_order = None
    
    for p in range(max_p + 1):
        for q in range(max_q + 1):
            if p == 0 and q == 0:  # Skip invalid GARCH(0, 0)
                continue
            
            try:
                # Fit GARCH model
                model = arch_model(data, vol='Garch', p=p, q=q, dist='normal')
                model_fit = model.fit(disp="off")
                
                # Check AIC
                if model_fit.aic < best_aic:
                    best_aic = model_fit.aic
                    best_order = (p, q)
            except Exception as e:
                log.error(f"Error fitting GARCH({p}, {q}): {e}")
                log.error(f"Choose ARIMA instead")                
                continue
    
    return best_order

# Functions for rolling forecast
def n_step_arima_forecast(data, n_steps):
    """
    Perform n-step recursive (rolling) forecast using ARIMA.
    :param data: Original time series data
    :param n_steps: Number of steps to forecast
    :return: List of n-step forecasts
    """
    arima_params = find_arima_parameters(data)
    model = ARIMA(data, order=arima_params)
    model_fit = model.fit()
    log.info("Model is fit")
    predictions = []
    history = data.copy() 
    
    for step in range(n_steps):
        # Predict one step ahead
        forecast = model_fit.forecast(steps=1)[0]
        predictions.append(forecast)
        log.info(f"Forecast for step {step + 1}: {forecast}")

        # Update history with the forecasted value
        history = np.append(history, forecast)
        
        # Refit the model using the updated history
        model = ARIMA(history, order=arima_params)
        model_fit = model.fit()
        
    return predictions

def n_step_garch_forecast(data, n_steps):
    """
    Perform n-step recursive (rolling) forecast using GARCH.
    :param data: Original time series data
    :param garch_params: GARCH parameters (p, q)
    :param n_steps: Number of steps to forecast
    :return: List of n-step forecasts
    """
    p, q = get_best_garch_params(data)  # GARCH(p, q)
    model = arch_model(data, vol='Garch', p=p, q=q, dist='normal')
    model_fit = model.fit(disp="off")
    
    # Initialize forecast list
    predictions = []
    history = data.copy()  # Simulate rolling updates

    for step in range(n_steps):
        # Forecast volatility for the next step
        forecast = model_fit.forecast(horizon=1)
        mean_forecast = forecast.mean['h.1'].iloc[-1]  # Mean forecast for the next step
        predictions.append(mean_forecast)
        
        # Update history with the forecasted value
        history = np.append(history, mean_forecast)
        
        # Refit the model with the updated history
        model = arch_model(history, vol='Garch', p=p, q=q, dist='normal')
        model_fit = model.fit(disp="off")
        
    return predictions

def n_step_sarima_forecast(data, n_steps):
    sarima_params, seasonal_order = find_arima_parameters(data, seasonal=True)
    model = SARIMAX(data, order=sarima_params, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
    model_fit = model.fit(disp=False)
    
    # Initialize the forecast list
    predictions = []
    history = data.copy()  # Make a copy of the data to simulate rolling updates
    
    for step in range(n_steps):
        # Predict one step ahead
        forecast = model_fit.forecast(steps=1)[0]
        predictions.append(forecast)
        
        # Update history with the forecasted value
        history = np.append(history, forecast)
        
        # Refit the model using the updated history
        model = SARIMAX(history, order=sarima_params, seasonal_order=seasonal_order, enforce_stationarity=False, enforce_invertibility=False)
        model_fit = model.fit(disp=False)
        
    return predictions

# Main MODEL training function
def train_arima_model(data, n_steps=1, seasonal = 0):
    """
    Train ARIMA models for each commodity, calculate rolling forecasts, and evaluate MEB.
    :param data: DataFrame of log-transformed commodity prices
    :param n_steps: Number of steps to forecast
    :param seasonal: control between garch, arima and sarima
    :return: MAPE of the final MEB forecast or forecast for n_steps
    """
    # Perform n-step forecast for future predictions
    if seasonal == 1:
        predictions = n_step_sarima_forecast(data, n_steps)
    elif seasonal == 0:
        predictions = n_step_arima_forecast(data, n_steps)
    else:
        predictions = n_step_garch_forecast(data, n_steps)
    # convert the log-transformed predictions back to the original scale
    predictions = np.exp(predictions)
    # print(f'Future forecast for {n_steps} steps:', predictions)
    return predictions
       

# Control function to manage data loading and model training
def model_controler(df_main, admin_label, chosen_cities, chosen_quantities, n_steps=1, seasonal = 0):
    """
    Control function to manage data loading and model training.
    :param df: DataFrame containing the data
    :param chosen_cities: List of cities to process
    :param chosen_quantities: List of commodities / products to process 
    :param n_steps: Number of steps to forecast / number of months
    :param seasonal: control between garch, arima and sarima
    :return: Single dataframe of forecasts for each city and commodity   
    """

    is_meb = False
    date_type = 'year_month'
    seasonal = 0 # control between garch, arima and sarima
    # Load data
    # get column names
    # convert list element to string
    # if admin_label is empty then set it as admin0_label
    # deep copy dataframe
    df = df_main.copy()
    if admin_label != "admin0_label":
        if "all" in chosen_cities or "ALL" in chosen_cities:
            chosen_cities = df[admin_label].unique()
    
    if "meb" in chosen_quantities or "MEB" in chosen_quantities:
        is_meb = True
        chosen_quantities = PRODUCTS_LABELS

        
    df[date_type] = pd.to_datetime(df[date_type], errors='coerce')

    # Convert 'date' to datetime and sort for time-series modeling

    overall_forecast = {}
    # Loop over each city and each commodity, make sure, it is not admin0_label 
    if admin_label != "admin0_label":
        filtered_df = df.sort_values(by=[admin_label, date_type])

        # Filter the data to include only the chosen cities and commodities
        filtered_df = filtered_df[filtered_df[admin_label].isin(chosen_cities)][[date_type, admin_label] + chosen_quantities]

        for city in chosen_cities:
            city_df = filtered_df[filtered_df[admin_label] == city]
            commodity_forecast = {}

            for commodity in chosen_quantities:
                log.info(f"Processing {commodity} for {city}...")

                # Extract time series for the current city and commodity
                ts_data = city_df[[date_type, commodity]].set_index(date_type)[commodity]
                ts_data = ts_data.replace(0, 1e-9).fillna(method='ffill').fillna(method='bfill')
                ts_data_log = np.log(ts_data).replace([np.inf, -np.inf], np.nan).dropna()

                # Train a model and calculate MEB forecast MAPE
                # Perform n-step future forecasting
                forecast = train_arima_model(ts_data_log, n_steps=n_steps, seasonal=seasonal)
                # convert forecast to a dictionary
                commodity_forecast[commodity] = forecast

            
            
            # convert commodity_forecast as a dataframe with date, admin_label and prices as columns
            forecast_df = pd.DataFrame(commodity_forecast)
            forecast_df[date_type] = pd.date_range(
                start=ts_data.index[-1], 
                periods=len(forecast_df) + 1, 
                freq='MS'
            )[1:]
            forecast_df[admin_label] = city
            forecast_df = forecast_df[[admin_label, date_type] + chosen_quantities]
            overall_forecast[city] = forecast_df
        # combine all forecasted dataframes into a single dataframe
        overall_forecast = pd.concat(overall_forecast.values(), ignore_index=True)
    
    else: # if it is admin0_label
        filtered_df = df.sort_values(by=[date_type])

        # Filter the data to include only the chosen commodities

        for commodity in chosen_quantities:

            log.info(f"Processing {commodity}... for {admin_label}")
            commodity_forecast = {}
            # Extract time series for the current commodity
            ts_data = filtered_df[[date_type, commodity]].set_index(date_type)[commodity]
            ts_data = ts_data.replace(0, 1e-9).fillna(method='ffill').fillna(method='bfill')
            ts_data_log = np.log(ts_data).replace([np.inf, -np.inf], np.nan).dropna()

            # Train a model and calculate MEB forecast MAPE
            # Perform n-step future forecasting
            forecast = train_arima_model(ts_data_log, n_steps=n_steps, seasonal=seasonal)
            # convert forecast to a dictionary

            # convert commodity_forecast as a dataframe with date, prices as columns
            forecast_df = pd.DataFrame(forecast, columns=[commodity])
            forecast_df[date_type] = pd.date_range(
                start=ts_data.index[-1], 
                periods=len(forecast_df) + 1, 
                freq='MS'
            )[1:]
            log.info(forecast_df.head())
            overall_forecast[commodity] = forecast_df
        # Start with an empty dataframe to accumulate the combined results
        overall_forecast_combined = None

        # Iterate through overall_forecast and merge dataframes
        for commodity, forecast_df in overall_forecast.items():
            if overall_forecast_combined is None:
                # Start with the first forecast dataframe
                overall_forecast_combined = forecast_df
            else:
                # Merge with the existing combined dataframe on the date column
                overall_forecast_combined = pd.merge(
                    overall_forecast_combined, 
                    forecast_df, 
                    on=date_type,  # Ensure the date column is the same
                    how='outer'    # Use outer join to include all dates
                )

        # Ensure the final dataframe is sorted by date
        overall_forecast = overall_forecast_combined.sort_values(by=date_type)

        # Reset index for a cleaner look
        overall_forecast.reset_index(drop=True, inplace=True)

    if is_meb:
        # Calculate MEB and store it in a new column
        overall_forecast = generate_average_meb(overall_forecast, admin_label)
        # reorder based on the date
        overall_forecast = overall_forecast.sort_values(by=[date_type])
        # keep only the date, meb and admin_label columns
        if admin_label != "admin0_label":
            overall_forecast = overall_forecast[[date_type, admin_label] + ['meb']]
        else:
            overall_forecast = overall_forecast[[date_type, 'meb']]
    return overall_forecast 
    
def plot_results(results, filtered_df, admin_label, chosen_cities, chosen_quantities):
    """
    Plot the original data and all three forecasts for each city and commodity on the same plot.
    
    :param main_results: List of forecast dictionaries from three different methods.
    :param filtered_df: Original filtered DataFrame containing actual values.
    :param chosen_cities: List of cities to process.
    :param chosen_quantities: List of commodities to process.
    """
    date_type = 'year_month'
    filtered_df[date_type] = pd.to_datetime(filtered_df[date_type])
    results[date_type] = pd.to_datetime(results[date_type])

    if admin_label != "admin0_label":
        for city in chosen_cities:
            city_data = filtered_df[filtered_df[admin_label] == city]
            results = results[results[admin_label] == city]
            for commodity in chosen_quantities:
                # Extract actual data
                actual_data = city_data[[date_type, commodity]].set_index(date_type)[commodity]
                actual_data = actual_data.replace(0, 1e-9).fillna(method='ffill').fillna(method='bfill')

                plt.figure(figsize=(12, 6))

                # Plot actual data
                plt.plot(actual_data.index, actual_data, label='Actual Data', linestyle='-', marker='o')

                # Plot forecasts from each method
                forecast_data = results[[date_type, commodity]].set_index(date_type)[commodity]
                forecast_dates = pd.date_range(
                    start=actual_data.index[-1], 
                    periods=len(forecast_data) + 1, 
                    freq='MS'
                )[1:]

                plt.plot(
                    forecast_dates, forecast_data,
                    marker='x', linestyle='--', label='Forecasted Data', color='red'
                )

                # Add labels, legend, and title
                plt.title(f"{commodity.capitalize()} Prices in {city}")
                plt.xlabel("Date")
                plt.ylabel("Price")
                plt.legend()
                plt.grid()
                plt.show()
    else:
        for commodity in chosen_quantities:
            # Extract actual data
            actual_data = filtered_df[[date_type, commodity]].set_index(date_type)[commodity]
            actual_data = actual_data.replace(0, 1e-9).fillna(method='ffill').fillna(method='bfill')

            plt.figure(figsize=(12, 6))

            # Plot actual data
            plt.plot(actual_data.index, actual_data, label='Actual Data', linestyle='-', marker='o')

            # Plot forecasts from each method
            forecast_data = results[[date_type, commodity]].set_index(date_type)[commodity]
            forecast_dates = pd.date_range(
                start=actual_data.index[-1], 
                periods=len(forecast_data) + 1, 
                freq='MS'
            )[1:]

            plt.plot(
                forecast_dates, forecast_data,
                marker='x', linestyle='--', label='Forecasted Data', color='red'
            )

            # Add labels, legend, and title
            plt.title(f"{commodity.capitalize()} Prices")
            plt.xlabel("Date")
            plt.ylabel("Price")
            plt.legend()
            plt.grid()
            plt.show()

if __name__ == '__main__':
    admin_1_csv_path = '../../data/processed/imputed_admin0_label_full.csv'
    admin_2_csv_path = '../../../../admin_2_final_dataset.csv'
    # admin_3_csv_path = '../../../../admin_3_final_dataset.csv'
    admin_df = pd.read_csv(admin_1_csv_path)
    chosen_cities = ["Idleb", "Aleppo"]
    chosen_quantities = ["meb"]
    n_steps = 2
    admin_label = "admin0_label"
    results = model_controler(admin_df, admin_label, chosen_cities, chosen_quantities, n_steps, seasonal = 0)
    # plot original values vs predictions
    # plot_results(results, admin_df, admin_label, chosen_cities, chosen_quantities)

    print(results.head())
    # main_results = []

    # for i in range (0,3):
    #     results = model_controler(admin_df, chosen_cities, chosen_quantities, n_steps, seasonal = i)
    #     main_results.append(results)
    # Plot the results
    # filtered_df = pd.read_csv(admin_1_csv_path)
    