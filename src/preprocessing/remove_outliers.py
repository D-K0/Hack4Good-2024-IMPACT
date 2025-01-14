from set_up.constants import PRODUCTS_LABELS 
import numpy as np


import logging

log = logging.getLogger(__name__)  # Logger for this module

def detect_outliers(data_outlierless, columns_to_analyse):
    """
    Detects and replaces outliers in a given DataFrame group.

    Parameters:
    group : pandas.DataFrame
        A subset (monthly data) of the DataFrame for which outliers are detected .
    columns_to_analyse : list
        A list of columns to analyze for outliers.

    Returns:
    pandas.DataFrame
        The group DataFrame with outliers replaced by NaN.
    """
    data = data_outlierless.copy()

    # Iterate over each column specified for analysis
    for column in columns_to_analyse:
        alpha = 10  # Set a multiplier for the IQR method

        # Calculate the first and third quartiles
        q1 = data[column].quantile(0.15)  # 15th percentile
        q3 = data[column].quantile(0.85)  # 85th percentile
        iqr = q3 - q1  # Interquartile range
        lower_bound = q1 - alpha * iqr  # Calculate the lower bound for outlier detection
        upper_bound = q3 + alpha * iqr  # Calculate the upper bound for outlier detection

        # Set a minimum value for the lower bound to avoid excessively low values
        if lower_bound < (q1 / 20):
            lower_bound = q1 / 20

        # Set the identified outliers to NaN in the cleaned group
        data.loc[(data[column] < lower_bound) | (data[column] > upper_bound), column] = np.nan
    # Return the cleaned group with outliers replaced by NaN
    return data


def generate_outlierless_data(data):
    """
    Preprocesses a DataFrame by cleaning data, generating relevant subsets, and removing outliers.

    Parameters:
    data : pandas.DataFrame
        preprocessed data without outliers or average

    Returns:
    pandas.DataFrame
        A cleaned and processed DataFrame.
    """
    relevant_goods_data = data.copy()
    total_nan_before = relevant_goods_data.isna().sum().sum()  # Count NaN values before outlier removal
    
    # Apply the detect_outliers function to each group of data based on 'date'
    relevant_goods_data = relevant_goods_data.groupby('date').apply(detect_outliers, PRODUCTS_LABELS).reset_index(drop=True)

    total_nan_after = relevant_goods_data.isna().sum().sum()  # Count NaN values after outlier removal
    # Print the difference in the number of NaN values before and after outlier detection
    log.info("Outliers have been detected: %d", (total_nan_after - total_nan_before))

    # Return the cleaned and processed DataFrame
    return relevant_goods_data
