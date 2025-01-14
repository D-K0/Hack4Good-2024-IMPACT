from statsmodels.tsa.arima.model import ARIMA
import pmdarima as pm
import numpy as np


def arima_imputation_fn(df_cleaned, admin_label, nan_df):
   
    """
    This function performs a data imputation technique based on ARIMA time series fitting.

    Inputs:
        df_cleaned: This is a pandas DataFrame that does not contain any NaN values.

        nan_df: This pandas DataFrame must have exactly the same dimensions and ordering in the date and admin level columns. It contains NaN values. The only information extracted from this DataFrame is the position of these NaN values.
        Usually, nan_df is the original DataFrame, and df_cleaned is one where some imputation techniques have already taken place. These imputations are refined in this function to improve performance.
    """

    # Creating a copy of df to avoid modifying the original input
    df = df_cleaned.copy()

    price_columns = [col for col in df.columns if col not in ["year_month", admin_label]]

    # Find all unique values in the 'admin_level' column
    unique_admin_levels = df[admin_label].unique()

    # Convert the unique values into a list
    # This summarizes the specific admin locations into a single list
    admin_location_list = unique_admin_levels.tolist()  


    for ad in admin_location_list:    
        for price in price_columns:

            #Finding the indices of NaN values in nan_df that indicate all positions where there were once NaN values in df_cleaned
            sinlge_admin_level_df_copy = nan_df[nan_df[admin_label] == ad]
            single_good_admin_copy = sinlge_admin_level_df_copy[price]
            single_good_admin_copy = single_good_admin_copy.reset_index().drop(columns=["index"])

            # Finding the indices of NaN values in nan_df but only considering values from index 5 onward (6th value)
            local_nan_indices = single_good_admin_copy.index[single_good_admin_copy.isna()[single_good_admin_copy.columns[0]]] 
            local_nan_indices = local_nan_indices[local_nan_indices >= 5]  # Start imputation from the 6th value (index 5)


            #preparing cleaned_df that contains no nan values to fit ARIMA model
            sinlge_admin_level_df = df[df[admin_label] == ad]
            single_good_admin = sinlge_admin_level_df[price]
            single_good_admin = single_good_admin.reset_index().drop(columns=["index"])

            ############################
            # Log-Transformation anwenden
            log_transformed_data = np.log(single_good_admin + 1)  # +1, to avoid log(0)-Problem

            # Setze NaN-Werte nach der Log-Transformation auf 0
            log_transformed_data = log_transformed_data.fillna(0)
            ############################

            # Automatic model fitting with auto_arima on the log-transformed data
            auto_arima_model = pm.auto_arima(log_transformed_data, stepwise=False, seasonal=False)
            print(auto_arima_model)

            # Extract the order parameters from auto_arima and fit the ARIMA model
            order = auto_arima_model.order
            model = ARIMA(log_transformed_data, order=order)
            model_fit = model.fit()

            #Generate for each nan value a single prediction 
            for index in local_nan_indices:
                in_sample_predictions = model_fit.get_prediction(start=index, end=index)
                predicted_values = in_sample_predictions.predicted_mean

                # Undo log transformation
                predicted_values = np.exp(predicted_values) - 1

                #save prediction locally
                single_good_admin.iloc[index] = predicted_values


             #save predictions and find the correct indices in df
            admin_df_indices = df[df[admin_label] == ad].index
            df.loc[admin_df_indices, price] = single_good_admin.values


    return df

            
